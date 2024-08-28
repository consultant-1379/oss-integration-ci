#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

def bob = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    parameters {
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'eoadm100-user-credentials',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'eoadm100-docker-auth-config',
                description: 'ARM Docker secret')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
    }
    agent {
        label env.SLAVE_LABEL
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${GERRIT_REFSPEC}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            steps {
                sh "git submodule sync"
                sh "git submodule update --init --recursive --remote"
                sh "${bob} git-clean"
            }
        }
        stage('Build and Push Spin Mgt Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                        sh "${bob} publish-pipeline-mgt-dev-image"
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
