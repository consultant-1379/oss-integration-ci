#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 *   + c12a011-config-file (admin.config to access c12a011 cluster)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '50', daysToKeepStr: '12', numToKeepStr: '120')
    }
    parameters {
        string(name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret')
        string(name: 'NAMESPACE',
            description: 'Namespace to install the Chart')
        string(name: 'KUBECONFIG_FILE',
            defaultValue: 'kube_config.yaml',
            description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST.')
        string(name: 'ENV_FILES_BUCKET_NAME',
            defaultValue: 'None',
            description: 'Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST.')
        string(name: 'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for a Functional user that has access to the data within DIT. ONLY USED if environment data store in OST.')
        string(name: 'COLLECT_LOGS_WITH_DM',
            defaultValue: 'false',
            description: 'If set to "false" (by default) - logs will be collected by ADP logs collection script. If true - with deployment-manager tool.')
        string(name: 'PATH_TO_AWS_FILES',
            defaultValue: 'NONE',
            description: 'Path within the Repo to the location of the AWS credentials and config directory')
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
    environment {
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${KUBECONFIG_FILE.split("-|_")[0]}"
                }
            }
        }
        stage('Checkout') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5')
                sh "${bob} git-clean"
                //Initialize parameters as environment variables due to https://issues.jenkins-ci.org/browse/JENKINS-41929
                evaluate """${def script = ""; params.each { k, v -> script += "env.${k} = '''${v}'''\n" }; return script}"""
            }
        }
        stage('Install docker config file') {
            steps {
                withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                    sh 'install -m 600 ${DOCKERCONFIG} ./dockerconfig.json'
                    sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                }
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
                BUCKET_OUTPUT_DIR = "kube_config"
            }
            steps {
                withCredentials([usernamePassword(credentialsId:params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-output-dir ost_bucket:download-all-files-in-ost-bucket"
                    sh "mv ./${BUCKET_OUTPUT_DIR}/${env.KUBECONFIG_FILE} ./${BUCKET_OUTPUT_DIR}/config"
                    sh "chmod 600 ./${BUCKET_OUTPUT_DIR}/config"
                }
            }
        }
        stage('Fetch Kube Config From Jenkins Credentials') {
            when {
                environment ignoreCase:true, name: 'ENV_FILES_BUCKET_NAME', value: 'none'
            }
            steps {
                withCredentials( [file(credentialsId:env.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh 'install -m 600 -D ${KUBECONFIG} ./kube_config/config'
                }
            }
        }
        stage('Copy AWS credentials for idun aaS') {
            when {
                not {
                    environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                }
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Retrieve Standard Logs') {
            when {
                allOf {
                    environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                    environment ignoreCase: true, name: 'COLLECT_LOGS_WITH_DM', value: 'true'
                }
            }
            steps {
                sh "${bob} gather-logs:gather-deployment-manager-logs || true"
            }
        }
        stage('Retrieve Standard Logs for idun aaS') {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                    }
                    environment ignoreCase: true, name: 'COLLECT_LOGS_WITH_DM', value: 'true'
                }
            }
            steps {
                sh "${bob} gather-logs:gather-deployment-manager-logs-idunaas || true"
            }
        }
        stage('Retrieve Detailed Logs') {
            when {
                environment ignoreCase: true, name: 'COLLECT_LOGS_WITH_DM', value: 'false'
            }
            steps {
                sh "${bob} gather-logs:gather-adp-k8s-logs || true"
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts allowEmptyArchive: true, artifacts: 'logs_*.tgz, logs/*', fingerprint: true
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
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