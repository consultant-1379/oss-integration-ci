pipeline {
    parameters {
        credentials(
            name: 'KUBECONFIG',
            description: 'Select kubeconfig to connect to cluster.'
            )
        credentials(
            name: 'REGISTRY_CREDENTIALS',
            description: 'Registry credentials.'
            )
        string(
            name: 'AGENT_LABEL',
            defaultValue: 'fem5dockerslave8',
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
    }
    agent {
          label "${params.AGENT_LABEL}"
    }
    stages {
        stage('Run registry cleanup') {
            agent {
                 docker {
                    image 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:latest'
                    reuseNode true
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS, usernameVariable: 'REGISTRY_USERNAME', passwordVariable: 'REGISTRY_PASSWORD')]) {
                sh """
                bash -c 'ci/jenkins/scripts/cleanup_env_registry.sh ${REGISTRY_USERNAME} ${REGISTRY_PASSWORD} ${KUBECONFIG}'
                """
                }
            }
        }
    }
}