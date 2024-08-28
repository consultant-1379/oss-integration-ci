#!/bin/bash
set -o nounset
set -o errexit

NAMESPACE=$1
KUBECONFIG=$2

echo "Started deletion of unused pvcs in namespace ${NAMESPACE}"
kubectl get pvc --kubeconfig "${KUBECONFIG}" -n "${NAMESPACE}" --no-headers=true | awk '{print $1}' | while read -r pvc
do
  if kubectl describe --kubeconfig "${KUBECONFIG}" -n "${NAMESPACE}" pvc "${pvc}" | grep "Used By:" | grep "<none>"
  then
    echo "pvc ${pvc} is unused, deleting it"
    kubectl delete pvc --kubeconfig "${KUBECONFIG}" "${pvc}" -n "${NAMESPACE}"
  fi
done
echo "Completed deletion of unused pvcs in namespace ${NAMESPACE}"