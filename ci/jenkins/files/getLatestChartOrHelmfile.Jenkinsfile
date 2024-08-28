#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string(name: 'INT_CHART_VERSION', defaultValue: '0.0.0', description: 'The version of the Integration Chart of Helmfile sent in through a previous jenkins build\'s artifact.properties.')
        string(name: 'INT_CHART_REPO', defaultValue: 'https://arm.epk.ericsson.se/artifactory/proj-eo-helm/', description: 'The repository in which the Integration chart or Helmfile will be stored.')
        string(name: 'INT_CHART_NAME', defaultValue: 'eo', description: 'The name of the Integration Chart or Helmfile to be searched')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Specify the slave label that you want the job to run on')
        string(name: 'FUNCTIONAL_USER_SECRET', defaultValue: 'ciloopman-user-creds', description: 'Jenkins secret ID for ARM Registry Credentials')
        string(name: 'ARMDOCKER_USER_SECRET', defaultValue: 'ciloopman-docker-auth-config', description: 'ARM Docker secret')
        string(name: 'FUNCTIONAL_USER_TOKEN', defaultValue: 'NONE', description: 'Jenkins identity token credential for ARM Registry access')
        string(name: 'SUBMODULE_SYNC_TIMEOUT', defaultValue: '60', description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT', defaultValue: '300', description: 'Number of seconds before the submodule update command times out')
        string(name: 'SPINNAKER_PIPELINE_ID', defaultValue: '123456', description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string(name: 'TIMEOUT', defaultValue: '3600', description: 'Time to wait in seconds before the job should timeout')
        string(name: 'CI_DOCKER_IMAGE', defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default', description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC', defaultValue: 'refs/heads/master', description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Prepare') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                    }
                }
            }
        }
        stage('Get Latest CHART or HelmFile Version') {
            steps {
                script{
                    if(params.FUNCTIONAL_USER_TOKEN.trim().toUpperCase() == "NONE" || params.FUNCTIONAL_USER_TOKEN.trim().isEmpty()){
                        withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh '''
                                if [[ ${INT_CHART_VERSION} != "0.0.0" ]]; then
                                    echo "INT_CHART_VERSION:${INT_CHART_VERSION}" > artifact.properties
                                else
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml get-latest-helmfile-version
                                fi
                            '''
                        }
                    }else{
                        withCredentials([string(credentialsId: params.FUNCTIONAL_USER_TOKEN, variable: 'FUNCTIONAL_USER_TOKEN')]) {
                            sh '''
                                if [[ ${INT_CHART_VERSION} != "0.0.0" ]]; then
                                    echo "INT_CHART_VERSION:${INT_CHART_VERSION}" > artifact.properties
                                else
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml get-latest-helmfile-version
                                fi
                            '''
                        }
                    }
                }
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
                    archiveArtifacts artifacts: "ci-script-executor-logs/*", allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
}

def get_ci_docker_image_url(ci_docker_image) {
    if (ci_docker_image.contains("default")) {
        String latest_ci_version = readFile "VERSION_PREFIX"
        String trimmed_ci_version = latest_ci_version.trim()
        url = ci_docker_image.split(':');
        return url[0] + ":" + trimmed_ci_version;
    }
    return ci_docker_image
}

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}

def command_timeout(time_and_unit, command) {
    /**
    Method to add a timeout to a command

    Input:
    time_and_unit: A string in the format <amount_of_time><unit_of_time> e.g. 5m for five minutes
    command: The shell command to run e.g. git submodule sync
    */

    def timeout_command = "timeout " + time_and_unit + " " + command
    def exit_status_of_command = sh(script: timeout_command, returnStatus: true)

    if (exit_status_of_command == 124) {
        echo 'The following command timed-out: ' + command
        // Fail the build
        sh(script: 'exit 124')
    }
}
