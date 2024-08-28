#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 *   + c12a011-config-file (admin.config to access c12a011 cluster)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'NAMESPACE',
            defaultValue: 'oss-deploy',
            description: 'Namespace to purge environment')
        string(name: 'KUBECONFIG_FILE',
            description: 'Kubernetes configuration file to specify which environment purge' )
        string(name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on')
        string(name: 'IGNORE_IF_CREATED',
            defaultValue: 'false',
            description: 'Used to ignore if the namespace is already created do not fail the job')
        string(name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:latest',
            description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'CLUSTER_ID',
            defaultValue: '',
            description: 'For internal CI testing. Unique identifier for dynamic cluster, usually the pipeline ID when invoked from Spinnaker')
        string(name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Set build name for dynamic cluster') {
            when {
                not {
                    environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                }
            }
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${CLUSTER_ID}"
                }
            }
        }
        stage('Set build name') {
            when {
                environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
            }
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${KUBECONFIG_FILE.split("-|_")[0]}"
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
        stage('Build Python-CI Scripts Image') {
            when {
                environment ignoreCase: true, name: 'CI_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
            }
        }
        stage('Initiate Dynamic Cluster') {
            when {
                not {
                    environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                }
            }
            steps {
                sh "${bobInternal} get-dynamic-cluster"
            }
        }
        stage('Setup Cluster Kubeconfig') {
            when {
                environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
            }
            steps {
                withCredentials( [file(credentialsId: env.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh "install -m 600 ${KUBECONFIG} ./admin.conf"
                }
            }
        }
        stage('Create Namespace') {
            steps {
                sh "${bob} create-namespace"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
