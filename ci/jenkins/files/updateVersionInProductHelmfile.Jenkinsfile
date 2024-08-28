#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
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
        string(name: 'GERRIT_PROJECT',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss.aeonic/oss-integration-ci')
        string(name: 'GERRIT_BRANCH',
                defaultValue: 'master',
                description: 'Gerrit branch the review should be submitted to, default: master')
        string(name: 'COMMIT_MESSAGE_FORMAT_MANUAL',
                defaultValue: 'NO JIRA - Version Prefix updated',
                description: 'Gerrit commit message to attach to the review')
        string(name: 'PREFIX_VERSION',
                description: 'This is the parameter for taking in the version to be set in the file')
        string(name: 'WAIT_SUBMITTABLE_BEFORE_PUBLISH',
                defaultValue: 'true',
                description: 'Executes a check against the review to ensure the review is submittable i.e. has a +1 verified and +2 Code Review. Options true or false')
        string (name: 'WAIT_TIMEOUT_SEC_BEFORE_PUBLISH',
                defaultValue: '1800',
                description: 'The amount of time the script will wait for the review to become submittable, this is used when WAIT_SUBMITTABLE_BEFORE_PUBLISH is set to true')
        string (name: 'CODE_REVIEW_ONLY',
                defaultValue: 'false',
                description: 'If set to false a Verified +1 label and a Code-Review +2 label is applied to the review. If set to true, only a Code-Review +2 label is applied.')
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'eoadm100-docker-auth-config',
                description: 'ARM Docker secret')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'The amount of time to wait in seconds for all the submodules to clone when executing the \"gerrit clone\" command')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'The amount of time to wait in seconds when executing the \"submodule update\" command')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Build Python-CI Scripts Image') {
            when {
                environment ignoreCase: true, name: 'CI_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
                script {
                    env.CI_DOCKER_IMAGE = "local:latest"
                }
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
        stage('Create a new review with new prefix version') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} gerrit:clone-repo"
                        sh "cd .bob/cloned_repo; sed -i 's/tag:.*/tag: \"\'${env.PREFIX_VERSION}\'\"/' helmfile/dm_version.yaml"
                        sh "${bob} gerrit:create-patch"
                    }
                }
            }
        }
        stage('Set Review Labels') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        withEnv(readFile('gerrit_create_patch.properties').split('\n') as List) {
                            sh "${bob} gerrit:set-review-labels gerrit:review-change gerrit:check-code-submittable"
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
                    archiveArtifacts artifacts: 'gerrit_create_patch.properties', allowEmptyArchive: true, fingerprint: true
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

    // Ensuring that seconds are used as the unit by adding an 's' to the time_and_unit
    def timeout_command = "timeout " + time_and_unit + " " + command
    def exit_status_of_command = sh(script: timeout_command, returnStatus: true)

    if (exit_status_of_command == 124) {
        echo 'The following command timed-out: ' + command
        // Fail the build
        sh(script: 'exit 124')
    }
}