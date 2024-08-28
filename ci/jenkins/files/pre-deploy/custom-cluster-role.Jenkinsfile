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
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'NAMESPACE',
            defaultValue: 'oss-deploy',
            description: 'Namespace to purge environment')
        string(name: 'KUBECONFIG_FILE',
            defaultValue: 'kube_config.yaml',
            description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST.')
        string(name: 'ENV_FILES_BUCKET_NAME',
            defaultValue: 'None',
            description: 'Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST.')
        string(name: 'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for a Functional user that has access to the data within DIT. ONLY USED if environment data store in OST.')
        string(name: 'RELEASE_NAME',
            defaultValue: 'eric-oss-commmon-base',
            description: 'Release name to be added to the file example <meta.helm.sh/release-name: <RELEASE_NAME>-<NAMESPACE_NAME>')
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
        string(name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${RELEASE_NAME} ${KUBECONFIG_FILE.split("-|_")[0]}"
                }
            }
        }
        stage('Clean Workspace') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
                //Initialize parameters as environment variables due to https://issues.jenkins-ci.org/browse/JENKINS-41929
                evaluate """${def script = ""; params.each { k, v -> script += "env.${k} = '''${v}'''\n" }; return script}"""
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
        stage ('Fetch Kube Config using OST') {
            when {
                not {
                    environment ignoreCase:true, name: 'ENV_FILES_BUCKET_NAME', value: 'none'
                }
            }
            environment {
                BUCKET_NAME = "${params.ENV_FILES_BUCKET_NAME}"
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                withCredentials([usernamePassword(credentialsId:params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-output-dir ost_bucket:download-all-files-in-ost-bucket"
                    sh "mv ./${env.KUBECONFIG_FILE} ./admin.conf"
                    sh "chmod 600 ./admin.conf"
                }
            }
        }
        stage('Fetch Kube Config From Jenkins Credentials') {
            when {
                environment ignoreCase:true, name: 'ENV_FILES_BUCKET_NAME', value: 'none'
            }
            steps {
                withCredentials( [file(credentialsId:env.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh "install -m 600 ${KUBECONFIG} ./admin.conf"
                }
            }
        }
        stage('Create cluster Role') {
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Create cluster Role\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Create cluster Role\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} generate-cluster-role:cluster-role"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
    }
    post {
        always {
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

