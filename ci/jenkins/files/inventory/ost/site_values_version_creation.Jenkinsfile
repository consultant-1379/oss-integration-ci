#!/usr/bin/env groovy

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
            description: 'Project Helmfile Name'
        )
        string(
            name: 'HELMFILE_VERSION',
            description: 'Project Helmfile Version'
        )
        string(
            name: 'SITE_VALUES_FILE_LATEST',
            defaultValue: 'site-values-latest.yaml',
            description: 'Name of the site values template to use to create the versioned site values from, including the file extension'
        )
        string(
            name: 'SITE_VALUES_FILE_LATEST_BUCKET_NAME',
            description: 'Name of the bucket that is storing the site values file latest that is stored in object store.'
        )
        string(
            name: 'SITE_VALUES_FILE_VERSIONED_BUCKET_NAME',
            description: 'Name of the bucket that is storing the site values versioned version that will be stored in object store.'
        )
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            description: 'Functional user that has access to all appropriate buckets in object store. The user creds should be stored in the Jenkins credentials area.'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret that is stored in the Jenkins credentials area.'
        )
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
            defaultValue: 'evo_docker_engine',
            description: 'Specify the Jenkins Agent label that the job should run on'
        )
        string(
            name: 'CI_GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )

    }
    environment {
        SITE_VALUES_FILE_VERSIONED_NAME = "site_values-${params.HELMFILE_VERSION}.yaml"
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker_configs"
        SITE_VALUES_FILE_NAME_STRIPPED = strip_file_extension("${params.SITE_VALUES_FILE_NAME}")
        DIT_SITE_VALUES_OUTPUT = "ost_site_values_output.txt"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${env.SITE_VALUES_FILE_VERSIONED_NAME}"
                }
            }
        }
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
        stage ('Check Site values version') {
            environment {
                BUCKET_NAME = "${params.SITE_VALUES_FILE_VERSIONED_BUCKET_NAME}"
                DATAFILE_NAME = strip_file_extension("${env.SITE_VALUES_FILE_VERSIONED_NAME}")
                DATAFILE_TYPE = get_file_extension("${env.SITE_VALUES_FILE_VERSIONED_NAME}")
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                retry(count: 3){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            def exitCode = sh (script: 'cat ${DIT_SITE_VALUES_OUTPUT} | grep "Object Not Found"', returnStatus: true)
                            if (exitCode == 0) {
                                echo "Site Values version does not exist"
                                currentBuild.result = 'SUCCESS'
                                RETRY_ATTEMPT = 1
                                env.SITE_VALUES_VERSION_EXIST = "0"
                                return
                            }
                            exitCode = sh (script: 'cat ${DIT_SITE_VALUES_OUTPUT} | grep "is downloaded."', returnStatus: true)
                            if (exitCode == 0) {
                                echo "Site Values version already exist, exiting..."
                                currentBuild.result = 'FAILURE'
                                sh "exit 1"
                            }
                            echo "Rerunning the \"Check Site values version\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Check Site values version\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-datafile-name ost_bucket:set-output-dir ost_bucket:download-files-by-name-in-ost-bucket"
                            sh "cat ${WORKSPACE}/${DIT_SITE_VALUES_OUTPUT}"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage ('Fetch CI Latest Site Values') {
            when {
                environment ignoreCase:true, name: 'SITE_VALUES_VERSION_EXIST', value: '0'
            }
            environment {
                BUCKET_NAME = "${params.SITE_VALUES_FILE_LATEST_BUCKET_NAME}"
                DATAFILE_NAME = strip_file_extension("${params.SITE_VALUES_FILE_LATEST}")
                DATAFILE_TYPE = get_file_extension("${params.SITE_VALUES_FILE_LATEST}")
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                retry(count: 3){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Fetch CI Latest Site Values\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Fetch CI Latest Site Values\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-datafile-name ost_bucket:set-output-dir ost_bucket:download-files-by-name-in-ost-bucket"
                            sh "cat ${WORKSPACE}/${DIT_SITE_VALUES_OUTPUT}"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage ('Upload Versioned Site Values File') {
            when {
                environment ignoreCase:true, name: 'SITE_VALUES_VERSION_EXIST', value: '0'
            }
            environment {
                BUCKET_NAME = "${params.SITE_VALUES_FILE_VERSIONED_BUCKET_NAME}"
                DATAFILE_NAME = strip_file_extension("${env.SITE_VALUES_FILE_VERSIONED_NAME}")
                DATAFILE_TYPE = get_file_extension("${env.SITE_VALUES_FILE_VERSIONED_NAME}")
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                retry(count: 3){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Upload Versioned Site Values File\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Upload Versioned Site Values File\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        env
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-datafile-name ost_bucket:set-output-dir ost_bucket:create-document-in-ost-bucket"
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

def get_ci_docker_image_url(ci_docker_image) {
    if (ci_docker_image.contains("default")) {
        String latest_ci_version = readFile "VERSION_PREFIX"
        String trimmed_ci_version = latest_ci_version.trim()
        url = ci_docker_image.split(':');
        return url[0] + ":" + trimmed_ci_version;
    }
    return ci_docker_image
}

def strip_file_extension(parameter) {
    return parameter.take(parameter.lastIndexOf('.'))
}

def get_file_extension(parameter) {
    return parameter.substring(parameter.lastIndexOf('.') + 1)
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


