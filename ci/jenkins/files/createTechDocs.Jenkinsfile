def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'AWS_REGION',
               defaultValue: 'eu-west-1',
               description: 'specify AWS region')
        string(name: 'TECHDOCS_BUCKET_NAME',
               defaultValue: 'techdocs',
               description: 'The name of the BUCKET where docs are stored')
        string(name: 'ENTITY_NAMESPACE',
               defaultValue: 'default',
               description: 'Namespace on cluster')
        string(name: 'ENTITY_NAME',
               description: 'Needs to match with catalog-info:metadata:name from the GERRIT_PROJECT')
        string(name: 'ENTITY_KIND',
               description: 'Should be set to the same value as kind property in the catalog-info.yaml eg.component or system ')
        string(name: 'MINIO_ENDPOINT',
               defaultValue: 'http://osmn.kroto020.rnd.gic.ericsson.se',
               description: 'Endpoint to use to connect to a minIO bucket')
        string(name: 'ARMDOCKER_USER_SECRET',
               description: 'ARM Docker secret')
        string(name: 'GERRIT_REFSPEC',
               defaultValue: 'refs/heads/master',
               description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
        string(name: 'GERRIT_USER_SECRET',
               description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'GERRIT_PROJECT',
               description: 'Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base')
        string(name: 'GERRIT_BRANCH',
               defaultValue: 'master',
               description: 'Gerrit branch the review should be submitted to, default: master')
        string(name: 'TIMEOUT',
               defaultValue: '3600',
               description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
               defaultValue: '60',
               description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
               defaultValue: '300',
               description: 'Number of seconds before the submodule update command times out')
    }
    environment {
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        AWS_SECRET_ACCESS_KEY = credentials('NM_IDP_AWS_SECRET_ACCESS_KEY')
        AWS_ACCESS_KEY_ID = credentials('NM_IDP_AWS_ACCESS_KEY_ID')
    }
    stages {
        stage('Prepare') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    retry(count: 5){
                        script {
                            if (RETRY_ATTEMPT > 1) {
                                echo "Rerunning the \"Install Docker Config\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                sleep(180)
                            }
                            else {
                                echo "Running the \"Install Docker Config\" stage. Try ${RETRY_ATTEMPT} of 5"
                            }
                            RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                            withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                                sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                            }

                            RETRY_ATTEMPT = 1
                        }
                    }
                }
            }
        }
        stage('Fetch Repo') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Fetch Repo\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                            sh "rm -rf .bob/cloned_repo"
                        }
                        else {
                            echo "Running the \"Fetch Repo\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bobInternal} gerrit:clone-repo-restricted"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage("TechDocs") {
            environment{
                HOME = "${env.WORKSPACE}/.bob/cloned_repo/"
            }
            steps {
                script {
                    sh "${bob} techdocs"
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
