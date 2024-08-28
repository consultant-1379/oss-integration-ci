#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
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
        string(name: 'NAMESPACE',
            description: 'Namespace on the cluster that the deployment is installed into.' )
        string(name: 'KUBECONFIG_FILE',
            defaultValue: 'kube_config.yaml',
            description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST.')
        string(name: 'ENV_FILES_BUCKET_NAME',
            defaultValue: 'None',
            description: 'Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST.')
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
            description: 'Label of the Jenkins slave where this jenkins job should be executed.')
        string(name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: 'ciloopman-user-creds',
            description: 'ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password.')
        string(name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret')
        string(name: 'INT_CHART_NAME',
            defaultValue: 'eric-eiae-helmfile',
            description: 'Name of the Product Helmfile that is used to list the releases and their versions.')
        string(name: 'INT_CHART_VERSION',
            description: 'Version of the Product Helmfile used to fetch the correct helmfile from artifactory.')
        string(name: 'INT_CHART_REPO',
            defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description: 'Repo to use when fetching the helmfile.')
        string(name: 'PATH_TO_HELMFILE',
            defaultValue: 'eric-eiae-helmfile/helmfile.yaml',
            description: 'Location of the helmfile within the helmfile artifact that has been downloaded.')
        string(name: 'TAGS',
            defaultValue: 'so pf uds adc th dmm eas',
            description: 'List of tags, used to ensure that the correct applications are deployed on the system with the correct version. Space separated list.' )
        string(name: 'OPTIONAL_TAGS',
            defaultValue: '',
            description: 'List of optional application tags (Example: SEF Application), used to ensure that the correct applications are deployed on the system with the correct version. Space separated list.' )
        string(name: 'OPTIONAL_KEY_VALUE_LIST',
            defaultValue: 'None',
            description: 'Optional comma separated list of additional key/value pairs to be added to site values. Each key level should be separated by \'.\' and value by \'=\' , e.g. eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false')
        string(name: 'CHECK_TAGS',
            defaultValue: '',
            description: 'List of specific tags to use for comparing deployed vs. helmfile chart-versions. Space separated list.' )
        string(name: 'CHECK_FULL_VERSION',
            defaultValue: 'false',
            description: 'Set to true if full chart version should be used instead of sprint version for application checks.' )
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
        stage('Cleaning Git Repo') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
                //Initialize parameters as environment variables due to https://issues.jenkins-ci.org/browse/JENKINS-41929
                evaluate """${def script = ""; params.each { k, v -> script += "env.${k} = '''${v}'''\n" }; return script}"""
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
        stage('Check Status of the Helmfile Deployment') {
            steps {
                script {
                    sh "${bob} check-helmfile-deployment-status:check-status"
                }
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'artifact.properties, site-values-updated.yaml', allowEmptyArchive: true, fingerprint: true
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