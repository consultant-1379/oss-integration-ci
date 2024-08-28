pipeline {
    parameters {
        credentials(
            name: 'KUBECONFIG',
            defaultValue: 'N239-config-file',
            description: 'kubeconfig to connect to cluster'
            )
        string(
            name: 'NAMESPACE',
            defaultValue: 'eo-openshift-deploy',
            description: 'Namespace where EO is deployed'
            )
        string(
            name: 'AGENT_LABEL',
            defaultValue: 'fem5dockerslave7',
            description: 'Label of jenkins agent where job should be executed'
            )
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'refs to use'
            )
    }
    environment {
        KUBECONFIG = credentials("${params.KUBECONFIG}")
        NAMESPACE = "${params.NAMESPACE}"
    }
     agent {
        docker {
          image 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:latest'
          label "${params.AGENT_LABEL}"
        }
    }
    stages {
        stage('VM VNFM post-upgrade procedure') {
            steps {
                sh """
                kubectl -n ${NAMESPACE} rollout restart sts eric-vnflcm-service-ha
                kubectl -n ${NAMESPACE} delete pvc service-data-eric-vnflcm-service-0 || true
                sleep 60
                ready_replicas=\$(kubectl -n ${NAMESPACE} get statefulset eric-vnflcm-service-ha -o jsonpath='{.status.readyReplicas}')
                until [[ ("\$ready_replicas" -eq "2") ]]; do
                   echo "-waiting until all eric-vnflcm-service-ha pods are in running state"
                   ready_replicas=\$(kubectl -n ${NAMESPACE} get statefulset eric-vnflcm-service-ha -o jsonpath='{.status.readyReplicas}')
                sleep 5
                done
                echo "eric-vnflcm-service-ha restarted."
                """
            }
        }
    }
}