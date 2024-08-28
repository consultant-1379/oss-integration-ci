#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */


def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'USE_DIT',
            defaultValue: 'false',
            description: 'Set to true or false, if set to true will fetch the environment details from DIT.')
        string(name: 'ENV_NAME',
            description: 'Name of the Environment to Gather details for. This should match your pooled environment in RPT or Jenkins lockable resources.')
        string(name: 'ENV_DETAILS_DIR',
            defaultValue: 'honeypots/pooling/environments',
            description: 'Location to search for environment details associated to the ENV_NAME, Not used if environment details stored in DIT.')
        string(name: 'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for a Functional user that has access to the data within DIT.')
        string(name: 'SPINNAKER_PIPELINE_ID',
            defaultValue: '123456',
            description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string(name: 'TIMEOUT',
            defaultValue: '3600',
            description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on')
        string(name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Clean Workspace') {
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Clean Workspace\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Clean Workspace\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                        command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob eo-integration-ci oss-common-ci')
                        sh "${bob} git-clean"
                        //Initialize parameters as environment variables due to https://issues.jenkins-ci.org/browse/JENKINS-41929
                        evaluate """${def script = ""; params.each { k, v -> script += "env.${k} = '''${v}'''\n" }; return script}"""
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Gather Environment Details using DIT') {
            when {
                environment ignoreCase:true, name: 'USE_DIT', value: 'true'
            }
            environment {
                DEPLOYMENT_NAME = "${params.ENV_NAME}"
            }
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Gather Environment Details\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Gather Environment Details\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} dit:set-document-name dit:download-document-from-dit"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Gather Environment Details using GIT') {
            when {
                environment ignoreCase:true, name: 'USE_DIT', value: 'false'
            }
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Gather Environment Details\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Gather Environment Details\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} gather-environment-details"
                        RETRY_ATTEMPT = 1
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
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
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