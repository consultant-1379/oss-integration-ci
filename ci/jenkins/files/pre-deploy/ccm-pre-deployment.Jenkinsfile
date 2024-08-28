pipeline {
    parameters {
        booleanParam(
            name: 'DELETE_CONFIGMAPS',
            defaultValue: true,
            description: 'Option to execute or skip stage of configmaps deletion. Cleanroom CPI art 4.5.1.1'
            )
         booleanParam(
            name: 'DELETE_JOBS',
            defaultValue: true,
            description: 'Option to execute or skip stage of all jobs deletion. Cleanroom CPI art 4.5'
            )
        credentials(
            name: 'KUBECONFIG',
            defaultValue: 'flexi32204-config-file',
            description: 'kubeconfig to connect to cluster'
            )
        string(
            name: 'NAMESPACE',
            defaultValue: 'cm-deploy',
            description: 'Namespace where CM is deployed'
            )
        string(
            name: 'AGENT_LABEL',
            defaultValue: 'fem5dockerslave8',
            description: 'Label of jenkins agent where job should be executed'
            )
        string(
            name: 'CM_SITENAME',
            defaultValue: 'sitename1',
            description: 'cCM sitename'
            )
         string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'refs to execute'
            )
    }
    environment {
        KUBECONFIG = credentials("${params.KUBECONFIG}")
        NAMESPACE = "${params.NAMESPACE}"
        CM_SITENAME = "${params.CM_SITENAME}"
    }
    agent {
        label "${params.AGENT_LABEL}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${params.KUBECONFIG.split("-|_")[0]}"
                }
            }
        }
        stage('cCM pre-deploy: Delete jobs') {
            when {
                beforeAgent true
                environment name: 'DELETE_JOBS', value: 'true'
                }
            agent {
                docker {
                    image 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:latest'
                    reuseNode true
                }
            }
            steps {
                sh '''
                kubectl -n $NAMESPACE delete job $(kubectl -n $NAMESPACE get jobs | grep -v NAME | awk '{print $1}') || true
                '''
            }
        }
        stage('cCM pre-deploy: Delete configmaps') {
            when {
                beforeAgent true
                environment name: 'DELETE_CONFIGMAPS', value: 'true'
                }
            agent {
                docker {
                    image 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:latest'
                    reuseNode true
                }
            }
            steps {
                sh '''
                for component in eric-eo-cm-cust-wf eric-eo-cm-onboarding
                do
                for cmapname in leader sync config
                do
                if kubectl -n $NAMESPACE get configmap $component-db-$CM_SITENAME-$cmapname; then
                kubectl -n $NAMESPACE delete configmap $component-db-$CM_SITENAME-$cmapname
                fi
                done
                done
                '''
            }
        }
    }
}