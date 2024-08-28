#!/bin/bash

KUBECONFIG=$1
NAMESPACE=$2
retries="30";
while [ $retries -ge 0 ]
do
    if [[ "$retries" -eq "0" ]]
    then
        echo PVs failed to remove please investigate
        exit 1
    elif kubectl get pv --kubeconfig "${KUBECONFIG}" | grep -q "${NAMESPACE}";
    then
        (( retries-=1 ))
        echo PVs remain, Retries left = $retries :: Sleeping for 60 seconds
        sleep 60
    else
        echo All PVs Removed
        break
    fi
done
