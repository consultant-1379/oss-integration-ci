#!/bin/bash

KUBECONFIG=$2
NAMESPACE=$1

delete_pods () {
  echo "Deleting pods"
  for i in $(kubectl -n "$NAMESPACE" get pods --kubeconfig "$KUBECONFIG" | grep eric-eo-cm-onbo |grep -v 'onboarding-db-' | awk '{print $1}');
  do
    kubectl -n "$NAMESPACE" delete pod "$i" --kubeconfig "$KUBECONFIG";
  done
}

until [[ -n $(kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get secret/eric-eo-cm-onboarding-docker-registry-tls -o yaml) ]];
  do
  echo "checking if secret is created"
  sleep 90
done

until [[ $(kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get secret/eric-eo-cm-onboarding-docker-registry-tls -o yaml | yq-4.x e '.data."docker-registry.crt"| length' - )  -eq 0 ]];
  do
  echo "checking if secret is empty..."
  sleep 90
done

kubectl -n "$NAMESPACE" apply -f ./ci/jenkins/resources/docker-reg-secret-eocm.yaml --kubeconfig "$KUBECONFIG"
kubectl -n "$NAMESPACE" apply -f ./ci/jenkins/resources/helm-reg-secret-eocm.yaml --kubeconfig "$KUBECONFIG"

delete_pods

