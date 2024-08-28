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
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'INT_CHART_VERSION',
                description: 'The version of helmfile' )
        choice(name: 'INT_CHART_NAME',
                choices: ['eric-eiae-helmfile', 'eric-eo-helmfile', 'eric-ci-helmfile', 'eric-eoom-helmfile'],
                description: 'Integration Chart Name. Please choose the appropriate helmfile from the dropdown.' )
        choice(name: 'INT_CHART_REPO',
                choices: ['https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm', 'https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm/', 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm/', 'https://arm.seli.gic.ericsson.se/artifactory/proj-eo-snapshot-helm/'],
                description: 'Integration Chart Repo. Please choose the appropriate repo from the dropdown. Note EOs repo has reference to eo in the url. The first and second option are for full helmfiles for IDUN/EOOM and EO, respectively. The third and fourth options are for snapshot helmfiles for IDUN/EOOM and EO, respectively.' )
        string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
                description: 'Jenkins secret ID for ARM Registry Credentials')
        string(
            name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret'
        )
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'GET_ALL_IMAGES',
                defaultValue: 'true',
                description: 'Set a true or false boolean to state whether to gather all release info independent of state values file')
        string(name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'Number of seconds before the submodule update command times out')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        STATE_VALUES_FILE = "${params.INT_CHART_NAME}/build-environment/tags_true.yaml"
        PATH_TO_HELMFILE = "${params.INT_CHART_NAME}/helmfile.yaml"
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }

    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${params.INT_CHART_NAME} ${params.INT_CHART_VERSION}"
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
        stage('Build Python-CI Scripts Image') {
            when {
                environment ignoreCase: true, name: 'CI_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
            }
        }
        stage('Get Helmfile and extract') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} fetch-helmfile untar-and-copy-helmfile-to-workdir"
                }
            }
        }
        stage('Update repositories file') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                        sh "${bob} update-repositories-file"
                    }
                }
            }
        }
        stage('Get Release Information and save to files') {
            steps {
                sh "${bob} get-microservice-release-details-from-helmfile"
            }
        }
        stage('Get Images Shared Across Each Chart') {
            steps {
                sh "${bob} get-shared-images"
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'helmServicesContent.txt, helmfile_services_json_content.json, helmfile_shared_services_json_content.json, helmfile_shared_images.json, outdated_images_per_chart.json', allowEmptyArchive: true, fingerprint: true
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