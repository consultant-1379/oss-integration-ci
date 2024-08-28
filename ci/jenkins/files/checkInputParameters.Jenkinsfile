#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'CHART_NAME', description: 'Chart Name sent in through a jenkins artifact.properties.\n This take precedence over the parmaeter sent to the spinnaker pipeline')
        string(name: 'CHART_VERSION', description: 'Chart Version sent in through a jenkins artifact.properties.\n This take precedence over the parmaeter sent to the spinnaker pipeline')
        string(name: 'CHART_REPO', description: 'Chart REPO sent in through a jenkins artifact.properties.\n This take precedence over the parmaeter sent to the spinnaker pipeline')
        string(name: 'INT_CHART_VERSION', description: 'Integration Chart Version, sent in through a jenkins artifact.properties.\n This take precedence over the parmaeter sent to the spinnaker pipeline')
        string(name: 'PARA_CHART_NAME', description: 'Chart Name, sent into the pipeline as a parameter by executing the spinnaker pipeline directly')
        string(name: 'PARA_CHART_VERSION', description: 'Chart Version, sent into the pipeline as a parameter by executing the spinnaker pipeline directly')
        string(name: 'PARA_CHART_REPO', description: 'Chart Repo, sent into the pipeline as a parameter by executing the spinnaker pipeline directly')
        string(name: 'PARA_INT_CHART_VERSION', description: 'Integration Chart Version, sent into the pipeline as a parameter by executing the spinnaker pipeline directly')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Specify the slave label that you want the job to run on')
        string(name: 'TIMEOUT', defaultValue: '3600', description: 'Time to wait in seconds before the job should timeout')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Generate Deployment Properties') {
            steps {
                sh '''
                    if [[ ${CHART_NAME} != "" && ${CHART_NAME} != *"CHART_NAME"* ]]; then
                        echo "CHART_NAME=${CHART_NAME}" > artifact.properties
                        echo "CHART_VERSION=${CHART_VERSION}" >> artifact.properties
                        echo "CHART_REPO=${CHART_REPO}" >> artifact.properties
                        echo "INT_CHART_VERSION=${INT_CHART_VERSION}" >> artifact.properties
                    elif [[ ${PARA_CHART_NAME} != "" && ${PARA_CHART_NAME} != *"CHART_NAME"* ]]; then
                        echo "CHART_NAME=${PARA_CHART_NAME}" > artifact.properties
                        echo "CHART_VERSION=${PARA_CHART_VERSION}" >> artifact.properties
                        echo "CHART_REPO=${PARA_CHART_REPO}" >> artifact.properties
                        echo "INT_CHART_VERSION=" >> artifact.properties
                    else
                        echo "Issue with the parameters. Please investigate."
                        exit 1
                    fi
                '''
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'artifact.properties', allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        failure {
            script {
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
}
