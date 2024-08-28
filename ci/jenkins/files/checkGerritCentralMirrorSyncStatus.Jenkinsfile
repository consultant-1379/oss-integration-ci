#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT_GERRIT_SYNC_CHECK = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'GERRIT_PROJECT',
            defaultValue: 'OSS/com.ericsson.oss.eiae/eiae-helmfile.git',
            description: 'The Gerrit Project to check is synced between Gerrit Central and Gerrit Mirror')
        string(name: 'GERRIT_BRANCH',
            defaultValue: 'master',
            description: 'The branch of the Gerrit Project to check is synced between Gerrit Central and Gerrit Mirror')
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
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Check Gerrit Central and Mirror Sync Status') {
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT_GERRIT_SYNC_CHECK > 1) {
                            echo "Rerunning the \"Check Gerrit Central and Mirror Sync Status\" stage. Retry ${RETRY_ATTEMPT_GERRIT_SYNC_CHECK} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Check Gerrit Central and Mirror Sync Status\" stage. Try ${RETRY_ATTEMPT_GERRIT_SYNC_CHECK} of 5"
                        }
                        RETRY_ATTEMPT_GERRIT_SYNC_CHECK = RETRY_ATTEMPT_GERRIT_SYNC_CHECK + 1
                        sh "${bob} check-gerrit-central-and-mirror-in-sync"
                    }
                }
            }
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