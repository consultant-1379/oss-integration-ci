#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 *   + c12a011-config-file (admin.config to access c12a011 cluster)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.AGENT_LABEL
    }
    parameters {
        string(
            name: 'HELMFILE_NAME',
            description: 'The name of the helmfile e.g. eric-eiae-helmfile' )
        string(
            name: 'HELMFILE_VERSION',
            description: 'The version of helmfile' )
        string(
            name: 'HELMFILE_REPO',
            description: 'Artifactory url to download the file from' )
        string(
            name: 'CHART_NAME',
            description: 'Helm Chart Name' )
        string(
            name: 'CHART_VERSION',
            description: 'Helm Chart Version' )
        string(
            name: 'CHART_REPO',
            description: 'Helm Chart Repo' )
        string(
            name: 'PATH_TO_HELMFILE',
            description: 'Path to the helmfile')
        choice(
            name: 'PROJECT_FILE_NAME',
            choices: ['None', 'eric-eiae-helmfile', 'eric-eo-helmfile', 'eric-eo-cm-helmfile'],
            description: 'Name of the project chart, e.g. eric-eiae-helmfile')
        string(
            name: 'SPINNAKER_PIPELINE_ID',
            defaultValue: '123456',
            description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for ARM Registry Credentials')
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret')
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
            name: 'AGENT_LABEL',
            description: 'Specify the Jenkins agent label that you want the job to run on')
        string(
            name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        EXECUTION_TYPE = set_execution_type("${params.CHART_NAME}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        INT_CHART_NAME = "${params.HELMFILE_NAME}"
        INT_CHART_VERSION = "${params.HELMFILE_VERSION}"
        INT_CHART_REPO = "${params.HELMFILE_REPO}"
    }
    stages {
        stage('Prepare') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Prepare\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Prepare\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                        command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                        sh "${bob} git-clean"
                        withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                            sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Run Parallel config steps'){
            parallel{
                stage('Get Helmfile and extract') {
                    steps {
                        retry(count: 5){
                            script{
                                if (RETRY_ATTEMPT > 1) {
                                    echo "Rerunning the \"Get Helmfile and extract\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(180)
                                }
                                else {
                                    echo "Running the \"Get Helmfile and extract\" stage. Try ${RETRY_ATTEMPT} of 5"
                                }
                                RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                                    sh "${bob} fetch-helmfile untar-and-copy-helmfile-to-workdir"
                                }
                                RETRY_ATTEMPT = 1
                            }
                        }
                    }
                }
                stage('Set Input file with Chart details') {
                    when {
                        expression { env.EXECUTION_TYPE == "set_baseline" }
                    }
                    steps {
                        script {
                            sh '''
                                echo "CHART_NAME=${CHART_NAME}" > input.properties
                                echo "CHART_VERSION=${CHART_VERSION}" >> input.properties
                                echo "CHART_REPO=${CHART_REPO}" >> input.properties
                            '''
                        }
                    }
                }
            }
        }
        stage('Get Application Version and save to artifact.properties') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Get Application Version and save to artifact.properties\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Get Application Version and save to artifact.properties\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} helmfile-details:get-set-version-details-for-base-baseline"
                        RETRY_ATTEMPT = 1
                    }
                }
                script {
                    sh '''
                        echo "BASE_PLATFORM_BASELINE_NAME=${HELMFILE_NAME}" >> artifact.properties
                        echo "BASE_PLATFORM_BASELINE_VERSION=${HELMFILE_VERSION}" >> artifact.properties
                        echo "BASE_PLATFORM_BASELINE_REPO=${HELMFILE_REPO}" >> artifact.properties
                    '''
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

def set_execution_type(chart_name) {
    if ( chart_name != '' ) {
        return "set_baseline"
    }
    return "get_baseline"
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
