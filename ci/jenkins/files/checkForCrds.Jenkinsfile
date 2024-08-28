#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT_CRD_CHECK = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(
            name: 'CHART_NAME',
            description: 'Application Chart Name to check against'
        )
        string(
            name: 'CHART_VERSION',
            description: 'Chart version to retrieve from the repo'
        )
        string(
            name: 'CHART_REPO',
            description: 'Chart Repo to pull the application chart from'
        )
        string(
            name: 'HELMFILE_CHART_NAME',
            defaultValue: 'eric-eiae-helmfile',
            description: 'Helmfile Name'
        )
        string(
            name: 'HELMFILE_CHART_VERSION',
            defaultValue: '0.0.0',
            description: 'The version of the helmfile to download and extract. Use 0.0.0 to get the latest version'
        )
        string(
            name: 'HELMFILE_CHART_REPO',
            defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm/',
            description: 'Helmfile Repo'
        )
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: 'ciloopman-user-creds',
            description: 'Jenkins secret ID for ARM Registry Credentials'
        )
        string(
            name: 'FUNCTIONAL_USER_TOKEN',
            defaultValue: 'NONE',
            description: 'Jenkins identity token credential for ARM Registry access'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret'
        )
        string(
            name: 'SPINNAKER_PIPELINE_ID',
            defaultValue: '123456',
            description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.'
        )
        string(
            name: 'TIMEOUT',
            defaultValue: '3600',
            description: 'Time to wait in seconds before the job should timeout')
        string(
            name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out')
        string(
            name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out')
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on'
        )
        string(
            name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
    }
    environment {
        PROPERTIES_FILE = 'tar_file_base_dir_artifact.properties'
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
        // The 'Get Latest CHART or HelmFile Version' stage requires INT_CHART_REPO, INT_CHART_VERSION
        // and INT_CHART_NAME variables to function
        INT_CHART_REPO = "${params.HELMFILE_CHART_REPO}"
        INT_CHART_VERSION = "${params.HELMFILE_CHART_VERSION}"
        INT_CHART_NAME = "${params.HELMFILE_CHART_NAME}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${env.CHART_NAME} ${env.CHART_VERSION}"
                }
            }
        }
        stage('Prepare') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
                sh "mkdir -m 777 CRD"
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
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            write_latest_helmfile_version()
                        }
                    }else{
                        withCredentials([string(credentialsId: params.FUNCTIONAL_USER_TOKEN, variable: 'FUNCTIONAL_USER_TOKEN')]) {
                            write_latest_helmfile_version()
                        }
                    }
                }
            }
        }
        stage('Get Helmfile') {
            environment {
                HELMFILE_CHART_VERSION = read_latest_helmfile_version()
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} helmfile:fetch-helmfile helmfile:extract-helmfile"
                    // We Read the Properties file from extract-helmfile to get the environment variable TAR_BASE_DIR
                }
            }
        }
        stage('Check CRD details from helm chart') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT_CRD_CHECK > 1) {
                            echo "Rerunning the \"Check CRD details from helm chart\" stage. Retry ${RETRY_ATTEMPT_CRD_CHECK} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Check CRD details from helm chart\" stage. Try ${RETRY_ATTEMPT_CRD_CHECK} of 5"
                        }
                        RETRY_ATTEMPT_CRD_CHECK = RETRY_ATTEMPT_CRD_CHECK + 1

                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            // We Read the Properties file from extract-helmfile to get the environment variable TAR_BASE_DIR
                            withEnv(readFile('tar_file_base_dir_artifact.properties').split('\n') as List) {
                                sh "${bob} crds:check-for-crds"
                            }
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
                    archiveArtifacts allowEmptyArchive: true, artifacts: "crd_details_artifact.properties", fingerprint: true
                }
            }
        }
        failure {
            script {
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                    archiveArtifacts allowEmptyArchive: true, artifacts: "ci-script-executor-logs/*", fingerprint: true
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

def write_latest_helmfile_version() {
    sh """
        if [[ ${INT_CHART_VERSION} != "0.0.0" ]]; then
            echo "INT_CHART_VERSION:${INT_CHART_VERSION}" > artifact.properties
        else
            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml get-latest-helmfile-version
        fi
    """
}

def read_latest_helmfile_version() {
    String line = readFile "artifact.properties"
    String latest_version = line.trim().split(':')[1]
    return latest_version
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