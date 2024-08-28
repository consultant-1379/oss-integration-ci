#!/bin/sh
set -o nounset
set -o errexit
SUPPORTED_VERSIONS_FILE_PATH=$1
PATH_TO_READ_HELM_TEMPLATES_FROM=$2

echo "Running deprek8ion against the supported minor kubernetes versions"
MINOR_K8S_VERSIONS=$(awk -F. '{print $1 "." $2}' "${SUPPORTED_VERSIONS_FILE_PATH}" | sort -u)
echo "$MINOR_K8S_VERSIONS" | while read -r supported_version
do
    echo "Running deprek8ion against kubernetes version $supported_version"
    POLICY_FILE=/policies/kubernetes-${supported_version}.rego
    if [ -f "$POLICY_FILE" ]
    then
        set +o errexit
        CHECK_OUTPUT=$(/conftest test -p /policies "${PATH_TO_READ_HELM_TEMPLATES_FROM}/${supported_version}.0.yaml" --policy "/policies/kubernetes-${supported_version}.rego")
        EXIT_CODE=$?
        set -o errexit
        echo "$CHECK_OUTPUT"
        if [ $EXIT_CODE -ne 0 ]
        then
            echo "deprek8ion failed against kubernetes version $supported_version"
            exit 255
        fi
    else
        if [ "${supported_version}" = "1.21" ] || [ "${supported_version}" = "1.23" ]
        then
            echo "INFO: Deprek8ion is known to not have any list of deprecated objects for kubernetes version ${supported_version}"
        else
            echo "ERROR: No deprek8ion policy for kubernetes version $supported_version. Check if a newer version of deprek8ion supports this version"
            exit 255
        fi
    fi
done
