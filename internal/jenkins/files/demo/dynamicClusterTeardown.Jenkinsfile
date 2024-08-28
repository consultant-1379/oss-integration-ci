#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on')
        string(name: 'CLUSTER_ID',
            defaultValue: '',
            description: 'For internal CI testing. Unique identifier for dynamic cluster, usually the pipeline ID when invoked from Spinnaker')
        string(name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${CLUSTER_ID}"
                }
            }
        }
        stage('Clean Workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
                sh "${bob} git-clean"
            }
        }
        stage('Teardown Dynamic Cluster') {
            steps {
                sh "${bobInternal} teardown-dynamic-cluster"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
