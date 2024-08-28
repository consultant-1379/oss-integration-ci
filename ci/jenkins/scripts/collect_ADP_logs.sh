#!/bin/bash
# shellcheck disable=SC2086
# shellcheck disable=SC2181
# shellcheck disable=SC2046
# shellcheck disable=SC2196
# shellcheck disable=SC2006
# shellcheck disable=SC2188
# shellcheck disable=SC2126
# shellcheck disable=SC2115

############################################################################
# This is not the official version of the ADP logs collection script.
# This is a fork modified by user "ZOLEPAN", used in OSS AppStaging pipelines.
############################################################################

############################################################################
# Latest official script version can located here:
# https://eteamspace.internal.ericsson.com/pages/viewpage.action?spaceKey=ACD&title=Tools
############################################################################

#Fail if empty argument received
if [[ "$#" = "0" ]]; then
    echo "Wrong number of arguments"
    echo "Usage collect_ADP_logs.sh <Kubernetes_namespace>"
    echo "Optional: collect_ADP_logs.sh <Kubernetes_namespace> <hours/minutes/seconds_to_capture_to_current_time>"
    echo "ex:"
    echo "$0 default    #--- to gather the logs for namespace 'default'"
    echo "Optional: $0 default  30m   #--- to gather the last 30 min of logs for namespace 'default'"
    echo "Optional: $0 default  45s   #--- to gather the last 45 sec of logs for namespace 'default'"
    echo "Optional: $0 default  2h   #--- to gather the last  2 hours of logs for namespace 'default'"
    exit 1
fi


namespace=$1

# Validate namespace
kubectl get namespace $namespace &>/dev/null

if [ $? != 0 ]; then
  echo "ERROR: The namespace $namespace does not exist. You can use \"kubectl get namespace\" command to verify your namespace"
  echo -e $USAGE
  exit 1
fi

#Define time
time=0
if [[ "$#" = "2" ]]; then
        time=$2
fi
#Create a directory for placing the logs
log_base_dir=logs_${namespace}_$(date "+%Y-%m-%d-%H-%M-%S")
log_base_path=$PWD/${log_base_dir}
mkdir ${log_base_dir}
#Check if there is helm2  or helm3 deployment

# echo "Collect script 1.0.0" > $log_base_path/script_version.txt
helm version | head -1 >$log_base_path/helm_version.txt
if eval ' grep v3 $log_base_path/helm_version.txt'
then
        echo "HELM 3 identified"
        HELM='helm get all --namespace='${namespace}
else
        HELM='helm get --namespace='${namespace}
       echo $HELM
fi

get_describe_info() {
    echo "-Getting resources describe info-"

    des_dir=${log_base_path}/describe
    for attr in statefulsets \
                internalCertificates \
                crd \
                deployments \
                services \
                replicasets \
                endpoints \
                daemonsets \
                persistentvolumeclaims \
                configmap \
                pods \
                nodes \
                jobs \
                persistentvolumes \
                rolebindings \
                roles \
                secrets \
                serviceaccounts \
                storageclasses \
                ingresses \
                httpproxy
        do
            dir=`echo $attr | tr '[:lower:]' '[:upper:]'`
            mkdir -p ${des_dir}/$dir
            kubectl --namespace ${namespace} get $attr -o wide > ${des_dir}/$dir/_get_$attr.txt &
            echo "Getting describe information on $dir.."
            kubectl --namespace ${namespace}  describe  $attr > ${des_dir}/$dir/_describe_$attr.yaml &

            if [[ "$attr" == "pods" ]]; then
                echo '-Getting info for not ready pods-'
                kubectl --namespace ${namespace} get pods | \
                    grep -Pv '\s+([1-9]+[\d]*)\/\1\s+' | \
                    grep -v Completed > ${des_dir}/$dir/_get_not_ready_$attr.txt

                kubectl --namespace ${namespace} describe pods \
                    $(cat ${des_dir}/$dir/_get_not_ready_$attr.txt | grep -v NAME | awk '{print $1}') \
                    > ${des_dir}/$dir/_describe_not_ready_$attr.yaml
            fi
        done

    for attr in $( kubectl api-resources --verbs=list --namespaced --no-headers |egrep -vi "events|statefulsets|internalCertificates|crd|deployments|services|replicasets|endpoints|daemonsets|persistentvolumeclaims|configmap|pod|nodes|jobs|persistentvolumes|rolebindings|roles|secrets|serviceaccounts|storageclasses|ingresses|httpproxy"| sed 's/true/;/g'| awk -F\; '{print $2}'|sort -u)
        do
            dir=`echo $attr | tr '[:lower:]' '[:upper:]'`
            mkdir -p ${des_dir}/OTHER/$dir
            kubectl --namespace "${namespace}" get $attr  -o wide > ${des_dir}/OTHER/$dir/$attr.txt
            echo "Getting describe information on $dir.."
            for i in `kubectl --namespace "${namespace}" get $attr | grep -v NAME | awk '{print $1}'`
                do
                    kubectl --namespace "${namespace}"  describe  $attr  $i > ${des_dir}/OTHER/$dir/$i.yaml
                done &
        done
    wait
}
get_events() {
    echo "-Getting list of events -"
    event_dir=$log_base_path/describe/EVENTS
    mkdir -p $event_dir

    kubectl --namespace ${namespace} get events > $event_dir/events.txt
}
get_pods_logs() {
    echo "-Getting logs per POD-"

    logs_dir=${log_base_path}/logs
    mkdir -p ${logs_dir}/env
    kubectl --namespace ${namespace} get pods -o wide > ${logs_dir}/_kube_podstolog.txt
    for i in `kubectl --namespace ${namespace} get pods | grep -v NAME | awk '{print $1}'`
        do
            pod_status=$(kubectl --namespace ${namespace} get pod $i -o jsonpath='{.status.phase}')
            pod_restarts=$(kubectl --namespace ${namespace} get pod $i |grep -vi restarts|awk '{print $4}')
            for j in `kubectl --namespace ${namespace} get pod $i -o jsonpath='{.spec.containers[*].name}'`
                do
                    kubectl --namespace ${namespace} logs $i -c $j --since=$time> ${logs_dir}/${i}_${j}.txt

                    if [[ "$pod_restarts" -gt "0" ]]; then
                    kubectl --namespace ${namespace} logs $i -c $j -p > ${logs_dir}/${i}_${j}_prev.txt &2>/dev/null
                    fi
                    # Only exec Pod in Running state
                    if [[ "$pod_status" == "Running" ]]; then
                        kubectl --namespace ${namespace} exec  $i -c $j -- env > ${logs_dir}/env/${i}_${j}_env.txt
                    fi
                done &
            init_containers=$(kubectl --namespace ${namespace} get pod $i -o jsonpath='{.spec.initContainers[*].name}')
            for j in $init_containers
                do
                    kubectl --namespace ${namespace} logs $i -c $j --since=$time> ${logs_dir}/${i}_${j}.txt

                    if [[ "$pod_restarts" -gt "0" ]]; then
                    kubectl --namespace ${namespace} logs $i -c $j -p > ${logs_dir}/${i}_${j}_prev.txt &2>/dev/null
                    fi
                done &
        done
        wait
}

get_helm_info() {
    echo "-Getting Helm Charts for the deployments-"
    helm_dir=${log_base_path}/helm
    mkdir ${helm_dir}
    helm --namespace ${namespace} list -a -d > ${helm_dir}/_helm_deployments.txt

    for i in `helm --namespace ${namespace} list -a | grep -v NAME | awk '{print $1}'`
        do
            echo $HELM $i
            $HELM $i > ${helm_dir}/$i.txt
            helm get values --namespace=${namespace} $i > ${helm_dir}/${i}_user_values.txt
        done
}

cmm_log() {
    echo "-Verifying for CM logs -"
    cmm_log_dir=${log_base_path}/logs/cmm_log

    if (kubectl --namespace=${namespace} get pods | grep -i cm-med|grep Running)
      then
        mkdir ${cmm_log_dir}
        echo "CM Pods found running, gathering cmm_logs.."
          for i in `kubectl --namespace=${namespace} get pods | grep -i cm-med | awk '{print $1}'`
            do
               echo $i
              kubectl --namespace ${namespace} exec $i --  collect_logs > ${cmm_log_dir}/cmmlog_$i.tgz
            done
            #Checking for schemas and configurations
            POD_NAME=`kubectl --namespace ${namespace} get pods |grep cm-mediator|grep -vi notifier|head -1|awk '{print $1}'`
            kubectl --namespace ${namespace} exec $POD_NAME -- curl -X GET http://localhost:5003/cm/api/v1/schemas | json_pp > ${cmm_log_dir}/schemas.json
            kubectl --namespace ${namespace} exec $POD_NAME -- curl -X GET http://localhost:5003/cm/api/v1/configurations | json_pp >  ${cmm_log_dir}/configurations.json
            configurations_list=$(cat ${cmm_log_dir}/configurations.json | grep \"name\" | cut -d : -f 2 | tr -d \",)
            for i in $configurations_list
            do
                    kubectl --namespace ${namespace} exec $POD_NAME -- curl -X GET http://localhost:5003/cm/api/v1/configurations/$i|json_pp > ${cmm_log_dir}/config_$i.json
            done
            wait
    else
        echo "CM Containers not found or not running, doing nothing"
    fi
}

siptls_logs() {
    echo "-Verifying for SIP-TLS logs -"
    siptls_log_dir=${log_base_path}/logs/sip_kms_dced

    if (kubectl --namespace=${namespace} get pods | grep -i sip-tls)
      then
      mkdir ${siptls_log_dir}
        echo "SIP-TLS Pods found, gathering siptls_logs.."
          for i in `kubectl --namespace=${namespace} get pods | grep -i sip-tls | awk '{print $1}'`
            do
                echo $i
                kubectl --namespace ${namespace} exec $i -- /bin/bash /sip-tls/sip-tls-alive.sh && echo $? > ${siptls_log_dir}/alive_log_$i.out
                kubectl --namespace ${namespace} exec $i -- /bin/bash /sip-tls/sip-tls-ready.sh && echo $? > ${siptls_log_dir}/ready_log_$i.out
                kubectl logs --namespace ${namespace}  $i sip-tls > ${siptls_log_dir}/sip-tls_log__$i.out
                kubectl logs --namespace ${namespace}  $i sip-tls --previous > ${siptls_log_dir}/sip-tls-previous_log_$i.out
                kubectl --namespace ${namespace} exec $i -- env > ${siptls_log_dir}/env_log__$i.out
            done

            kubectl --namespace ${namespace} exec eric-sec-key-management-main-0 -c kms -- bash -c 'vault status -tls-skip-verify' > ${siptls_log_dir}/vault_status_kms.out
            kubectl --namespace ${namespace} exec eric-sec-key-management-main-0 -c shelter -- bash -c 'vault status -tls-skip-verify' > ${siptls_log_dir}/vault_status_shelter.out
            kubectl get crd --namespace ${namespace}  servercertificates.com.ericsson.sec.tls -o yaml  > ${siptls_log_dir}/servercertificates_crd.yaml
            kubectl get  --namespace ${namespace}  servercertificates -o yaml  > ${siptls_log_dir}/servercertificates.yaml
            kubectl get crd --namespace ${namespace}  clientcertificates.com.ericsson.sec.tls -o yaml  > ${siptls_log_dir}/clientcertificates_crd.yaml
            kubectl get  --namespace ${namespace}  clientcertificates -o yaml  > ${siptls_log_dir}/clientcertificates.out
            kubectl get crd --namespace ${namespace} certificateauthorities.com.ericsson.sec.tls -o yaml  > ${siptls_log_dir}/certificateauthorities_crd.yaml
            kubectl get  --namespace ${namespace}  certificateauthorities -o yaml  > ${siptls_log_dir}/certificateauthorities.out
            kubectl get  --namespace ${namespace}  internalcertificates.siptls.sec.ericsson.com  -o yaml  > ${siptls_log_dir}/internalcertificates.yaml
            kubectl get  --namespace ${namespace}  internalusercas.siptls.sec.ericsson.com  -o yaml  > ${siptls_log_dir}/internalusercas.yaml
            kubectl get secret --namespace ${namespace} -l com.ericsson.sec.tls/created-by=eric-sec-sip-tls > ${siptls_log_dir}/secrets_created_by_eric_sip.out
            pod_name=$(kubectl get po -n ${namespace} -l app=eric-sec-key-management -o jsonpath="{.items[0].metadata.name}")
            kubectl --namespace ${namespace} exec $pod_name -c kms -- env VAULT_SKIP_VERIFY=true vault status > ${siptls_log_dir}/kms_status_.out

    else
        echo "SIP-TLS Containers not found or not running, doing nothing"
    fi
}

cmy_log() {
    echo "-Verifying for CM Yang logs -"

    cmy_log_dir=${log_base_path}/logs/sssd_cmy_log

    if (kubectl --namespace=${namespace} get pods | grep -i yang|grep Running)
      then
        mkdir ${cmy_log_dir}
        echo "CM Yang Pods found running, gathering cmyang_logs.."
          for i in `kubectl --namespace=${namespace} get pods | grep -i yang | awk '{print $1}'`
            do
               echo $i
              #              kubectl --namespace ${namespace} logs $i confd -p  > ${cmy_log_dir}/confd_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i notification-sender -p  > ${cmy_log_dir}/notification-sender_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i yang-ext -p  > ${cmy_log_dir}/yang-ext_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i cpa -p  > ${cmy_log_dir}/cpa_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i ypint -p  > ${cmy_log_dir}/ypint_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i sshd -p  > ${cmy_log_dir}/sshd_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i ss -p  > ${cmy_log_dir}/ss_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i init-db -p  > ${cmy_log_dir}/init-db_previous_$i.txt
              #              kubectl --namespace ${namespace} logs $i confd   > ${cmy_log_dir}/confd_$i.txt
              #              kubectl --namespace ${namespace} logs $i notification-sender   > ${cmy_log_dir}/notification-sender_$i.txt
              #              kubectl --namespace ${namespace} logs $i yang-ext   > ${cmy_log_dir}/yang-ext_$i.txt
              #              kubectl --namespace ${namespace} logs $i cpa   > ${cmy_log_dir}/cpa_$i.txt
              #              kubectl --namespace ${namespace} logs $i ypint   > ${cmy_log_dir}/ypint_$i.txt
              #              kubectl --namespace ${namespace} logs $i sshd   > ${cmy_log_dir}/sshd_$i.txt
              #              kubectl --namespace ${namespace} logs $i ss   > ${cmy_log_dir}/ss_$i.txt
              #              kubectl --namespace ${namespace} logs $i init-db   > ${cmy_log_dir}/init-db_$i.txt
              mkdir ${logs_dir}/sssd_$i/
              kubectl --namespace ${namespace} cp $i:/var/log/sssd   ${logs_dir}/ssd_$i/ -c sshd
            done

    else
         echo "CM Yang Containers not found or not running, doing nothing"
    fi
}

function diameter_log (){
    DIA_POD=$(kubectl --namespace ${namespace} get pod -l app=eric-stm-diameter -o name)
    pod_status=$(kubectl --namespace ${namespace} get $DIA_POD -o jsonpath='{.status.phase}')
    if [[ "$pod_status" == "Running" ]]; then
        diacc=${log_base_path}/logs/dia
        mkdir $diacc
        kubectl --namespace $namespace exec $DIA_POD -- curl -s http://localhost:20100/dumpState > ${diacc}/dumpState.txt
        kubectl --namespace $namespace exec $DIA_POD -- curl -s http://localhost:20100/troubleshoot/transportDump/v2 > ${diacc}/transport.txt
        kubectl --namespace $namespace exec $DIA_POD -- curl -s http://localhost:20100/dumpConfig > ${diacc}/dumpConfig.txt
    fi
}

basic_checks () {
    mkdir  ${log_base_path}/logs/err
    mkdir  ${log_base_path}/logs/SE
    #    for i in `ls ${log_base_path}/logs/`
    #    do
    #            filename=`echo $i| awk '{print substr($1,1,length($1)-4)}'`
    #            cat ${log_base_path}/logs/$i | egrep -i "err|warn|crit" > ${log_base_path}/logs/err/$filename.err.txt
    #    done
     for i in ${log_base_path}/logs/
        do
            filename=`echo $i| awk '{print substr($1,1,length($1)-4)}'`
            log_path="${log_base_path}/logs/$i"
        if ! [ -d $log_path ]; then
            cat ${log_path} | egrep -i "err|warn|crit" > ${log_base_path}/logs/err/$filename.err.txt
            cat ${log_path} | egrep -i "failed to perform indices:data/write/bulk|latency|failed to send out heartbeat on time|disk|time out|timeout|timed out" > ${log_base_path}/logs/err/$filename.latency.txt
        fi
    done

    grep -B2 "Image:" ${log_base_path}/describe/PODS/_describe_pods.yaml | grep -v "Container ID:" > ${log_base_path}/describe/PODS/pods_image_versions.txt

    #SE_POD=$(kubectl --namespace ${namespace} get pod -l  "app=eric-data-search-engine,role in (ingest-tls,ingest)" -o jsonpath="{.items[0].metadata.name}")
    pod_status=$(kubectl --namespace ${namespace} get  pods | grep search-engine|wc -l)
    if [[ "$pod_status" -gt "0" ]]; then
        esRest="kubectl -n ${namespace} exec -c searchengine $(kubectl get pods -n ${namespace} -l "app=eric-data-search-engine,role in (ingest-tls,ingest)" -o jsonpath="{.items[0].metadata.name}") -- /bin/esRest"
        $esRest GET /_cat/nodes?v>${log_base_path}/logs/SE/nodes.txt
        $esRest GET /_cat/indices?v>${log_base_path}/logs/SE/indices.txt
        $esRest GET /_cluster/health?pretty > ${log_base_path}/logs/SE/health.txt
        $esRest GET /_cluster/allocation/explain?pretty > ${log_base_path}/logs/SE/allocation.txt
    fi
    mkdir ${log_base_path}/logs/sip_kms_dced/DCED
    for i in `kubectl --namespace ${namespace} get pod |grep data-distributed-coordinator-ed|grep -v agent|awk '{print $1}'`
    do
        echo $i
        kubectl --namespace ${namespace} exec $i -- etcdctl member list -w fields >  ${log_base_path}/logs/sip_kms_dced/DCED/memberlist_$i.txt
        kubectl --namespace ${namespace} exec $i -- bash  -c 'ls /data/member/snap -lh' >  ${log_base_path}/logs/sip_kms_dced/DCED/sizedb_$i.txt
        kubectl --namespace ${namespace} exec $i -- bash  -c 'du -sh data/*;du -sh data/member/*;du -sh data/member/snap/db' >>  ${log_base_path}/logs/sip_kms_dced/DCED/sizedb_$i.txt
        kubectl --namespace ${namespace} exec $i -- etcdctl  endpoint status --endpoints=:2379 --insecure-skip-tls-verify=true -w fields>  ${log_base_path}/logs/sip_kms_dced/DCED/endpoints_$i.txt
        kubectl --namespace ${namespace} exec $i -- etcdctl user list >  ${log_base_path}/logs/sip_kms_dced/DCED/user_list$i.txt
    done
    if (kubectl --namespace=${namespace} get pods | grep -i kvdb-ag); then
        mkdir ${log_base_path}/logs/KVDBAG

   for i in `kubectl --namespace ${namespace} get pods|grep -i kvdb-ag|awk '{print $1}'`
   do
        echo $i
        kubectl --namespace ${namespace} cp $i:/opt/dbservice/data/logs ${log_base_path}/logs/KVDBAG/dbservicedatalogs$i/
        kubectl --namespace ${namespace} cp $i:/opt/dbservice/data/stats ${log_base_path}/logs/KVDBAG/dbservicedatastats$i/
    done
  fi
}

compress_files() {
    echo "Generating tar file and removing logs directory..."
    tar cfz $PWD/${log_base_dir}.tgz ${log_base_dir}
    echo  -e "\e[1m\e[31mGenerated file $PWD/${log_base_dir}.tgz, Please collect and send to ADP Support!\e[0m"
    rm -r $PWD/${log_base_dir}
}

print_pods_info() {
    echo "-Print out pod's describe output-"

    helm_dir=${log_base_path}/helm
    des_dir=${log_base_path}/describe
    attr="pods"
    dir=`echo $attr | tr '[:lower:]' '[:upper:]'`

    echo "DEBUG: Printing list of Helm deployments"
    cat ${helm_dir}/_helm_deployments.txt
    echo "DEBUG: Printing list of PODs"
    cat ${des_dir}/$dir/_get_$attr.txt
    echo "DEBUG: Printing list of not ready PODs"
    cat ${des_dir}/$dir/_get_not_ready_$attr.txt
    echo "DEBUG: Printing not ready PODs describe output"
    cat ${des_dir}/$dir/_describe_not_ready_$attr.yaml
}

get_app_onboarding_logs() {
    echo "-Getting app onboarding logs-"
    app_onboarding=$(kubectl -n $namespace get po | grep onboarding | awk '{ print $1 }')
    if [[ -n "$app_onboarding" ]]; then
        mkdir -p ${log_base_dir}/app-onboarding
        for i in $app_onboarding
            do
            pod_status=$(kubectl --namespace ${namespace} get pod $i -o jsonpath='{.status.phase}')
            if [[ "$pod_status" == "Running" ]]; then
                kubectl cp $namespace/$i:/tmp/logs/jobs ${log_base_dir}/app-onboarding/$i/ # If 'tar' binary is not present, 'kubectl cp' will fail.
            else
                echo "POD $i is not in running state"
            fi
            done
    else
        echo "NO app-onboarding pod found, skip getting logs"
    fi
}

sm_log() {
    #echo "-----------------------------------------"
    echo "-Verifying for SM logs -"
    #echo "-----------------------------------------"
    #echo "-----------------------------------------"

    sm_log_dir=${log_base_path}/logs/sm_log
    serviceMeshCustomResources=("adapters.config" "attributemanifests.config" "authorizationpolicies.security" "destinationrules.networking" "envoyfilters.networking" "gateways.networking" "handlers.config" "httpapispecbindings.config" "httpapispecs.config" "instances.config" "peerauthentications.security" "proxyconfigs.networking" "quotaspecbindings.config" "quotaspecs.config" "rbacconfigs.rbac" "requestauthentications.security" "rules.config" "serviceentries.networking" "servicerolebindings.rbac" "serviceroles.rbac" "sidecars.networking" "telemetries.telemetry" "templates.config" "virtualservices.networking" "wasmplugins.extensions" "workloadentries.networking" "workloadgroups.networking")
    istioDebugURL=("adsz" "syncz" "registryz" "endpointz" "instancesz" "endpointShardz" "configz" "cachez" "resourcesz" "authorizationz" "push_status" "inject" "mesh" "networkz")
    proxyDebugURL=("certs" "clusters" "config_dump?include_eds" "listeners" "memory" "server_info" "stats/prometheus" "runtime")
    if (kubectl --namespace=${namespace} get pods --selector app=istiod | grep eric-mesh-controller | grep Running)
    then
      mkdir -p ${sm_log_dir}/istio
      echo "SM Controller pods found running, gathering sm_log for controller pods..."
      for pod_name in `kubectl --namespace=${namespace} get pods --selector app=istiod --no-headers | awk -F " " '{print $1}'`
        do
          mkdir -p ${sm_log_dir}/istio/$pod_name/debug
          for debug_path in "${istioDebugURL[@]}"
            do
              kubectl --namespace ${namespace} exec ${pod_name} -c discovery -- curl --silent http://localhost:15014/debug/${debug_path} > ${sm_log_dir}/istio/${pod_name}/debug/${debug_path}
            done &
        done
      if (kubectl --namespace=${namespace} get crd | grep istio.io >/dev/null)
      then
        echo "SM Controller CRDs have been found, looking for applied CRs..."
        for sm_crs in "${serviceMeshCustomResources[@]}"
          do
            if [[ $(kubectl --namespace ${namespace} get ${sm_crs}.istio.io --ignore-not-found) ]]
            then
              sm_cr=$(echo ${sm_crs} | awk -F "." '{print $1}')
              mkdir -p ${sm_log_dir}/ServiceMeshCRs/${sm_cr}
              echo "Applied ${sm_cr} CR has been found, gathering sm_log for it..."
              for resource in `kubectl --namespace ${namespace} get ${sm_crs}.istio.io --no-headers | awk -F " " '{print $1}'`
                do
                  kubectl --namespace ${namespace} get ${sm_crs}.istio.io ${resource} -o yaml > ${sm_log_dir}/ServiceMeshCRs/${sm_cr}/${resource}.yaml
                done &
            fi
          done
      else
        echo "No SM Controller CRD has been found!"
      fi
      if (kubectl --namespace=${namespace} get pods -o jsonpath='{.items[*].spec.containers[*].name}' | grep istio-proxy)
      then
        mkdir -p ${sm_log_dir}/proxies
        echo "Pods with istio-proxy container are found, gathering sm_log for pods with istio-proxy..."
        for pod_name in `kubectl --namespace=${namespace} get pods -o jsonpath='{range .items[*]}{"\n"}{.metadata.name}{": "}{range .spec.containers[*]}{.name}{" "}{end}{end}' | grep istio-proxy | awk -F ":" '{print $1}'`
          do
            mkdir ${sm_log_dir}/proxies/${pod_name}
            for debug_path in "${proxyDebugURL[@]}"
              do
                if [[ ${debug_path} == "stats/prometheus" ]]; then
                  mkdir ${sm_log_dir}/proxies/${pod_name}/stats
                fi
                kubectl --namespace ${namespace} exec ${pod_name} -c istio-proxy -- curl --silent http://localhost:15000/${debug_path} > ${sm_log_dir}/proxies/${pod_name}/${debug_path}
              done &
          done
      else
        echo "Pods with istio-proxy containers are not found or not running, doing nothing"
      fi
    else
       echo "ServiceMesh Controller pods are not found or not running, doing nothing"
    fi
    wait
}

get_helm_info &
get_describe_info &
get_events &
get_pods_logs &
cmm_log &
siptls_logs &
cmy_log &
diameter_log &
get_app_onboarding_logs &
sm_log &
wait
basic_checks
print_pods_info
compress_files
