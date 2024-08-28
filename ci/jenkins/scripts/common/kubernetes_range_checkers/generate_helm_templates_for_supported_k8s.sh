#!/bin/bash
set -o nounset
set -o errexit

CHART_OR_HELMFILE=$1
SITE_VALUES_FILE=$2
SUPPORTED_VERSIONS_FILE_PATH=$3
PATH_TO_WRITE_TEMPLATES_TO=$4

SCHEMAS_LOCATION='https://arm.seli.gic.ericsson.se/artifactory/proj-ecm-k8s-schema-generic-local'

get_supported_api_versions_for_k8s_version() {
    set -o nounset
    set -o errexit
    K8S_VERSION=$1
    # Tidy up of this is required as part of IDUN-10041
    all_json_url="${SCHEMAS_LOCATION}/v${K8S_VERSION}-standalone-strict/all.json"
    curl -f -o "all_${K8S_VERSION}.json" "${all_json_url}"
    versions_with_k8s_io=$(sed -n 's:^.*io\.k8s\.api\.\(.*\)\.\(.*\)\.\(.*\)"$:\1.k8s.io/\2/\3:gp' "all_${K8S_VERSION}.json")
    versions_without_k8s_io=${versions_with_k8s_io//.k8s.io/}
    versions_with_k8s_io_just_bases=$(echo "${versions_with_k8s_io}" | sed 's:\(.*/.*\)/.*:\1:g' | sort -u)
    versions_without_k8s_io_just_bases=$(echo "${versions_without_k8s_io}" | sed 's:\(.*/.*\)/.*:\1:g' | sort -u)
    echo "${versions_with_k8s_io}"
    echo "${versions_without_k8s_io}"
    echo "${versions_with_k8s_io_just_bases}"
    echo "${versions_without_k8s_io_just_bases}"
}

mkdir -p "${PATH_TO_WRITE_TEMPLATES_TO}"
MINOR_K8S_VERSIONS=$(awk -F. '{print $1 "." $2}' "${SUPPORTED_VERSIONS_FILE_PATH}" | sort -u)
echo "$MINOR_K8S_VERSIONS" | while read -r supported_version
do
    supported_version="${supported_version}.0"
    echo "Getting k8s api versions supported in version ${supported_version}"

    set +o errexit
    api_versions=$(get_supported_api_versions_for_k8s_version "${supported_version}")
    if [ -z "$api_versions" ]
    then
        echo "Could not find any supported version."
        exit 255
    fi
    set -o errexit

    echo "Rendering helm template for k8s version ${supported_version}"
    if [[ $(basename "${CHART_OR_HELMFILE}") == 'helmfile.yaml' ]]
    then
        KUBE_API_VERSIONS="$(echo "${api_versions}" | tr '\n' ',' | sed 's/,$//g')"
        export KUBE_API_VERSIONS
        echo "Environment variable KUBE_API_VERSIONS set to ${KUBE_API_VERSIONS}"
        command_to_run="helmfile --environment build --state-values-file ${SITE_VALUES_FILE} -f ${CHART_OR_HELMFILE} template --args '--kube-version ${supported_version}'"
    else
        helm_api_versions="$(echo "${api_versions}" | sed 's/^/--api-versions /g' | tr '\n' ' ')"
        command_to_run="helm template ${CHART_OR_HELMFILE} -f ${SITE_VALUES_FILE} ${helm_api_versions} --kube-version ${supported_version}"
    fi
    set +o errexit
    command_to_run_with_redirect_to_disk=$(${command_to_run} > "${PATH_TO_WRITE_TEMPLATES_TO}"/"${supported_version}".yaml)
    EXIT_CODE=$?
    set -o errexit
    echo "${command_to_run_with_redirect_to_disk}"
    if [ $EXIT_CODE -ne 0 ]
    then
        echo "Helm template tests failed"
        exit 255
    fi

done