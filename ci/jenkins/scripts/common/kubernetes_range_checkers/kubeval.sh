#!/bin/bash
set -o nounset
set -o errexit
SUPPORTED_VERSIONS_FILE_PATH=$1
PATH_TO_READ_HELM_TEMPLATES_FROM=$2
SKIP_KINDS="${3-}"

echo "Running kubeval against the oldest and newest supported kubernetes version"
OLDEST_SUPPORTED_VERSION=$(head -1 "$SUPPORTED_VERSIONS_FILE_PATH")
NEWEST_SUPPORTED_VERSION=$(tail -1 "$SUPPORTED_VERSIONS_FILE_PATH")

VERSIONS_TO_CHECK="
${OLDEST_SUPPORTED_VERSION}
${NEWEST_SUPPORTED_VERSION}
"

echo "$VERSIONS_TO_CHECK" | grep "\." | while read -r supported_version
do
    echo "Running Kubeval against kubernetes version $supported_version"
    set +o errexit
    OUTPUT=$(kubeval --skip-kinds "${SKIP_KINDS}" -v "$supported_version" --strict --force-color "${PATH_TO_READ_HELM_TEMPLATES_FROM}/${supported_version}.yaml" --additional-schema-locations https://arm.seli.gic.ericsson.se/artifactory/proj-ecm-k8s-schema-generic-local)
    EXIT_CODE=$?
    set -o errexit
    # Filter out invalid warning caused by issues in the checker scripts that need to be fixed in IDUN-10041
    OUTPUT=$(echo "$OUTPUT" | grep -v 'contains an invalid PodDisruptionBudget - apiVersion: apiVersion must be one of the following: "policy/v1beta1')
    # Filter out the warnings about the skipped kinds
    for kind in ${SKIP_KINDS//,/ }
    do
        echo "Filtering out warnings for kind $kind"
        OUTPUT=$(echo "$OUTPUT" | grep -v "${kind} was not validated against a schema")
    done
    echo "${OUTPUT}"
    if [[ $EXIT_CODE -ne 0 ]]
    then
        set +o errexit
        PASS_COUNT=$(echo "$OUTPUT" | grep -c "PASS")
        FAIL_COUNT=$(echo "$OUTPUT" | grep -c "FAIL")
        WARN_COUNT=$(echo "$OUTPUT" | grep -c "WARN")
        set -o errexit
        echo "Passed: $PASS_COUNT"
        echo "Failures: $FAIL_COUNT"
        echo "Warnings: $WARN_COUNT"
        if (( FAIL_COUNT > 0 )) || (( WARN_COUNT > 0 )) || (( PASS_COUNT == 0 ))
        then
            echo "kubeval failed against kubernetes version $supported_version"
            exit 255
        else
            echo "kubeval passed against kubernetes version $supported_version"
        fi
    else
        echo "kubeval passed against kubernetes version $supported_version"
    fi
done
