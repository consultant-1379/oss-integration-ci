#!/bin/bash
set -o nounset

KUBE_VERSION_FILE="${1}"
MIN_SUPPORTED_K8S_VERSION=$(grep kubeVersion "${KUBE_VERSION_FILE}" | awk '{print $2}')
MAX_SUPPORTED_K8S_VERSION=$(grep kubeVersion "${KUBE_VERSION_FILE}" | awk '{print $4}')
K8S_VERSION_GITHUB_TAGS=$(git ls-remote --tags https://github.com/kubernetes/kubernetes | grep -E -v 'beta|\^|alpha|-rc' | awk '{print $2}' | sed 's|refs/tags/v||g' | sort -V)
SUPPORTED_K8S_VERSIONS=$(echo "${K8S_VERSION_GITHUB_TAGS}" | grep -A 1000 "^${MIN_SUPPORTED_K8S_VERSION}$" | grep -B 1000 "^${MAX_SUPPORTED_K8S_VERSION}$")
EXIT_CODE=$?
echo "${SUPPORTED_K8S_VERSIONS}"
if [ $EXIT_CODE -ne 0 ]
then
    echo "print_supported_k8s_versions.sh failed"
    exit 255
fi
