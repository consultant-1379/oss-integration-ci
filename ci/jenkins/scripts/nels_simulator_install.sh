#!/bin/bash

# The idempotent script for instalation and configuration the NeLS simulator in a given namespace.
# If an existing installation is found in the namespace, the installation will be verified. In case of failure reinstallation is performed.

set -e

CHART_VERSION=$1
NAMESPACE=$2
KUBECONFIG=$3
FUNCTIONAL_USER_USERNAME=$4
FUNCTIONAL_USER_PASSWORD=$5
LICENSE_KEYS=$6
LICENSE_DATA=$7


if [[ -z $CHART_VERSION || -z $NAMESPACE || -z $KUBECONFIG || -z $FUNCTIONAL_USER_USERNAME || -z $FUNCTIONAL_USER_PASSWORD || -z $LICENSE_KEYS  || -z $LICENSE_DATA ]]; then
    cat << EOF
    ERROR: One or more required arguments not defined:

    - Chart version: NeLS chart version. If 0.0.0-0 the latest dev version will be used.

    - Namespace: namespace where NeLS sim need to be installed.

    - Kubeconfig: Kubernetes configuration file.

    - Functional user: for access to ARM registry.

    - functional user password: for access to ARM registry.

    - license keys: If 'true' the EIC License keys will be available.

    - license data: License keys data in json format

    Usage: $0 <chart version> <namespace> <kubeconfig> <functional user> <functional user password> <license keys> <license data>
EOF
  exit 1
fi

SCRIPT_PID=$$
trap 'exit 1' SIGTERM

nels_install () {

  echo "The NeLS simulator installation is starting..."
  echo "=========================================================="

  # Removing existing NeLS installation
  if robust_cmd helm list -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -q | grep internal-eric-test-nels-simulator; then
    robust_cmd helm uninstall internal-eric-test-nels-simulator -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" --wait
    echo "The existing NeLS sim installation deleted"
  fi

  # Removing existing configmap
  if robust_cmd kubectl get configmap -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep nels-magic; then
    robust_cmd kubectl delete configmap nels-magic -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "The existing nels-magic configmap in $NAMESPACE deleted"
  fi

  # Create docker secret for main namespace
  if ! robust_cmd kubectl get secret -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep nels-registry-secret; then
    robust_cmd kubectl create secret generic nels-registry-secret \
      --from-file=.dockerconfigjson="$PWD"/.docker/config.json \
      --type=kubernetes.io/dockerconfigjson \
      --namespace "$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "The docker ARM secret in $NAMESPACE namespace created"
  fi

  # Create Network policy for nels-simulator
  if ! robust_cmd kubectl get networkpolicy -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep eric-test-nels-simulator-allow-access; then
    cat > eric-test-nels-simulator-access.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: eric-test-nels-simulator-allow-access
spec:
  ingress:
  - from:
    - podSelector:
        matchLabels:
          eric-test-nels-simulator-access: "true"
    ports:
    - port: 9095
      protocol: TCP
  podSelector:
    matchLabels:
      app.kubernetes.io/name: eric-test-nels-simulator
  policyTypes:
  - Ingress
EOF
    robust_cmd kubectl apply -f eric-test-nels-simulator-access.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Network policy for nels-simulator created"
  fi

  # Add LS repo
  robust_cmd helm repo add nels-sim-repository --username "$FUNCTIONAL_USER_USERNAME" --password  "$FUNCTIONAL_USER_PASSWORD" https://arm.sero.gic.ericsson.se/artifactory/proj-adp-eric-test-nels-sim-helm

  # install LS
  if [[ $CHART_VERSION == "0.0.0-0" ]]; then
      # Install the latest dev version
      robust_cmd helm install internal-eric-test-nels-simulator nels-sim-repository/eric-test-nels-simulator --devel --set imageCredentials.pullSecret=nels-registry-secret -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" --wait
  else
      # Install specific version
      robust_cmd helm install internal-eric-test-nels-simulator nels-sim-repository/eric-test-nels-simulator --version "$CHART_VERSION" --set imageCredentials.pullSecret=nels-registry-secret -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" --wait
  fi
  echo "The NeLS sim has been successfully deployed"

  # get its pod
  LS_POD=$(robust_cmd kubectl get pods -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep eric-test-nels-simulator | sed 's#pod/##')
  echo "License Server pod is $LS_POD - sleep 10s"
  sleep 10

  # create LS
  robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl -s -i -w "\n" --header "Content-Type: application/json" --request POST http://localhost:8080/nels-management/servers --data '{"serverName" : "cNeLS-Simulator", "thriftPort" : "9095", "capabilities" : [ { "name": "ClientDrivenAggregation", "status": true}, { "name": "LicenseInfoIntegrity", "status": true}, { "name": "NegativeUsageReporting", "status": true}, { "name": "PersistentPeak", "status": true} ]}' >  ls_answer.txt

  # shellcheck disable=SC2002
  # get its LS_ID
  LS_ID=$(cat ls_answer.txt | grep -i Location | sed -r "s|[Ll]ocation: .*/(.+)\r$|\1|")
  echo "License Server ID is $LS_ID"

  # save LS_ID in a configmap for further consumption
  robust_cmd kubectl create configmap nels-magic -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" --from-literal=ls_id="${LS_ID}"

  # activate the LS
  robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl -s -w "\n" --header "Content-Type: application/json" --request PATCH http://localhost:8080/nels-management/servers/"$LS_ID" --data '{"status": "STARTED"}'
  echo "License Server has been activated - waiting 5 s"
  sleep 5

  # check successful activation
  robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl -s -w "\n" --header "Content-Type: application/json" http://localhost:8080/nels-management/servers/"$LS_ID"

  echo "The NeLS simulator installation completed successfully"
  if [[ $LICENSE_KEYS == "true" ]]; then
    add_license
  fi
}

nels_installation_check () {

  echo "Verification of NeLS simulator installation is starting..."
  echo "=========================================================="

  if ! (robust_cmd kubectl get configmap -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep nels-magic); then
    echo "Configmap nels-magic does not exist in $NAMESPACE namespace"
    return 1
  fi

  if ! (robust_cmd kubectl get pods -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep eric-test-nels-simulator); then
    echo "Required pod does not exist in $NAMESPACE namespace"
    return 1
  fi

  # get ls_id
  LS_ID=$(robust_cmd kubectl get cm nels-magic -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o jsonpath='{.data.ls_id}')
  echo "License Server ID is $LS_ID"

  # get pod
  LS_POD=$(robust_cmd kubectl get pods -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -o name | grep eric-test-nels-simulator | sed 's#pod/##')
  echo "License Server pod is $LS_POD"

  # check status
  response=$(robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl --output /dev/null -s -w "%{http_code}" -m 0.5 --header "Content-Type: application/json" \
    --request GET http://localhost:8080/nels-management/servers/"$LS_ID")
  echo "Status code of test request: $response"

  if [[ $response == 200 ]]; then
    return 0
  fi

  return 1
}

add_license () {
  echo "Adding license keys......"
  echo "=========================================================="
  # License configuration: customerId must be the same, likely the swltId, otherwise only one LKF is seen by LM
  # add license for EIC product

  echo "$LICENSE_DATA"

  robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl -s -w "\n" --header "Content-Type: application/json" --request POST http://localhost:8080/nels-management/servers/"${LS_ID}"/license-keys --data "$LICENSE_DATA"
}

remove_license () {
  echo "Deleting license keys..."
  echo "=========================================================="

  # Preparing data for a request to remove license keys
  del_data=$(echo "$LICENSE_DATA" | jq 'del(.keys)')
  echo "$del_data"

  # Removing license keys
  robust_cmd kubectl exec "$LS_POD" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -- \
    curl -s -w "\n" --header "Content-Type: application/json" --request DELETE http://localhost:8080/nels-management/servers/"${LS_ID}"/license-keys --data "$del_data"
}

# A wrapper function for the helm and kubectl commands to improve robustness.
robust_cmd () {

  retries=5

  while [ $retries -ge 0 ]; do

    if [[ $retries -eq 0 ]]; then
        echo "ERROR: Failed to execute '$*'" >&2
        echo "Execution terminated !" >&2
        kill -9 $SCRIPT_PID
        exit 1  # Exit from subshell
    fi

    if "$@"; then
        break
    else
        (( retries-- ))
        if ! [[ $retries -eq 0 ]]; then
            echo "Failed to execute '$*', Retries left = $retries :: Sleeping for 5 seconds" >&2
            if [[ $* = *'helm install'* ]] && robust_cmd helm list -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -q | grep internal-eric-test-nels-simulator; then
               # Remove failed release after try
               robust_cmd helm uninstall internal-eric-test-nels-simulator -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" --wait
               echo "Failed NeLS sim installation deleted"
            fi
            sleep 5
        fi
    fi
  done
}

echo "Checking if the NeLS sim is installed"
echo "=========================================================="
if robust_cmd helm list -n "$NAMESPACE" --kubeconfig "$KUBECONFIG" -q | grep internal-eric-test-nels-simulator; then
  echo "Installed release of NeLS sim was found in the $NAMESPACE namespace."

  if nels_installation_check; then
    echo "Verification successful. Reinstallation is not required"

    # Checking the need to add/remove LICENSE KEYS to an existing verified NeLS SIM installation.
    if [[ $LICENSE_KEYS == "true" ]]; then
        add_license
    else
        remove_license
    fi

  else
    echo "Verification failed. Reinstallation required"
    nels_install
  fi

else
  echo "NeLS sim release was not found in the $NAMESPACE namespace."
  nels_install
fi