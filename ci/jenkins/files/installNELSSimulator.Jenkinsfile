#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

def RETRY_ATTEMPT = 1

pipeline {
    parameters {
        string(
              name: 'NAMESPACE',
              description: 'Namespace where the application is running on the cluster')
        string(name: 'KUBECONFIG_FILE',
              defaultValue: 'hart123-kubeconfig',
              description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID')
        string(name: 'CHART_VERSION',
              defaultValue: '0.0.0-0',
              description: 'NeLS chart version. If 0.0.0-0 the latest dev version will be used.')
        string(name: 'LICENSE_KEYS',
              defaultValue: 'true',
              description: 'Availability of EIC license keys. If true the license keys will be added otherwise will be removed.')
        string(name: 'LICENSE_DATA',
              defaultValue: '{\\"productType\\":\\"EIC\\",\\"customerId\\":\\"800141\\",\\"swltId\\":\\"STB-EIC-2\\",\\"keys\\":[{\\"licenseId\\":\\"FAT1024424\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"},{\\"licenseId\\":\\"FAT1024425\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"},{\\"licenseId\\":\\"FAT1024426\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"},{\\"licenseId\\":\\"FAT1024429\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"},{\\"licenseId\\":\\"FAT1024431\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"},{\\"licenseId\\":\\"FAT1024518\\",\\"licenseType\\":\\"FEATURE\\",\\"start\\":\\"2023-11-10\\",\\"stop\\":\\"2033-11-09\\"}]}',
              description: 'License keys data in json format')
        string(name: 'FUNCTIONAL_USER_CREDENTIALS',
              defaultValue: 'ciloopman-user-creds',
              description: 'Jenkins secret to ARM')
        string(name: 'ARMDOCKER_USER_SECRET',
              defaultValue: 'ossapps100-arm-docker-auth-config',
              description: 'ARM Docker secret')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
              defaultValue: '60',
              description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
              defaultValue: '300',
              description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL',
              defaultValue: 'common_agents',
              description: 'Specify the slave label that you want the job to run on')
        string(name: 'CI_REFSPEC',
              defaultValue: 'refs/heads/master',
              description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
        string(name: 'TIMEOUT',
              defaultValue: '30',
              description: 'Execution timeout in mins')
    }
    environment {
        DOCKER_CONFIG = "${WORKSPACE}/.docker"
    }
    agent {
        label env.SLAVE_LABEL
    }
    options {
        timeout(time: env.TIMEOUT, unit: 'MINUTES')
    }
    stages {
        stage('Preparation stages in parallel'){
            parallel{
                stage('Set build name') {
                    steps {
                        script {
                            currentBuild.displayName = "${env.BUILD_NUMBER} ${params.KUBECONFIG_FILE.split("-|_")[0]} ${params.NAMESPACE}"
                        }
                    }
                }
                stage('Workplace preparation') {
                    steps {
                        retry(count: 5){
                            script{
                                if (RETRY_ATTEMPT > 1) {
                                    echo "Rerunning the \"Workplace preparation\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(180)
                                }
                                else {
                                    echo "Running the \"Workplace preparation\" stage. Try ${RETRY_ATTEMPT} of 5"
                                }
                                RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                                // Checkout submodule
                                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')

                                // Workspace cleanup
                                sh "${bob} git-clean"

                                RETRY_ATTEMPT = 1
                            }
                        }
                    }
                }
            }
        }
        stage('Fetch Kube and Docker Configs') {
            steps {
                withCredentials( [
                        file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG'),
                        file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')
                ]) {
                    sh "install -m 600 ${KUBECONFIG} ./admin.conf"
                    sh 'install -m 600 -D $DOCKERCONFIG $DOCKER_CONFIG/config.json'
                }
            }
        }
        stage('NeLS Install') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"NeLS Install\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"NeLS Install\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_CREDENTIALS, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "chmod +x ${env.WORKSPACE}/ci/jenkins/scripts/nels_simulator_install.sh"
                            sh "${bob} nels-simulator-install"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
    }
    post {
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