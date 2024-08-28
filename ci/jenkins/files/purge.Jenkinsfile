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
    agent {
        label env.SLAVE_LABEL
    }
    options{
        timeout(time: 30, unit: 'MINUTES')
    }
    parameters {
        string(name: 'NAMESPACE',
            defaultValue: 'oss-deploy',
            description: 'Namespace to purge deployment environment')
        string(name: 'CRD_NAMESPACE',
            defaultValue: 'eric-crd-ns',
            description: 'Namespace to purge CRD environment')
        string(name: 'CLEANUP_TYPE',
            defaultValue: 'PARTIAL',
            description: 'Selecting FULL will cleanup deployment helm releases, TLS secrets, Network Policies, Installed PVCs, Deployment namespace, CRD helm releases, CRD components and CRD namespace. Selecting PARTIAL will only cleanup deployment helm releases, TLS secrets, Network Policies, Installed PVCs and Deployment Namespace.')
        string(name: 'TIMEOUT_IN_SECONDS',
            defaultValue: '60',
            description: 'Option to alter the timeout in waiting for the deletion of pvcs - Will abort the job if it reaches the timeout')
        string(name: 'KUBECONFIG_FILE',
            defaultValue: 'kube_config.yaml',
            description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST.')
        string(name: 'ENV_FILES_BUCKET_NAME',
            defaultValue: 'None',
            description: 'Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST.')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on')
        string(name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret')
        string(name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: 'ciloopman-user-creds',
            description: 'Jenkins secret ID for ARM Registry Credentials')
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
        stage('Clean Workspace') {
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
        stage('Build Python-CI Scripts Image') {
            when {
                environment ignoreCase: true, name: 'CI_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
            }
        }
        stage('Remove All Helm Release From Namespace') {
            steps {
                retry(count: 3){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Remove All Helm Release From Namespace\" stage. Retry ${RETRY_ATTEMPT} of 3. Sleeping 20 seconds before retry..."
                            sleep(20)
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} remove-all-helm-releases-from-namespace"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Remove KafkaTopic Resources') {
            steps {
                script {
                    sh "${bob} remove-kt-resources"
                }
            }
        }
        stage('Temporary Workaround to cleanup AppMgr onboarding jobs') {
            // Temporary workaround until AppMgr bug is fixed IDUN-105013
            steps {
                retry(count: 3){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Temporary Workaround to cleanup AppMgr onboarding jobs\" stage. Retry ${RETRY_ATTEMPT} of 3. Sleeping 20 seconds before retry..."
                            sleep(20)
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        sh """
                            docker run --init --rm \
                            --volume ${WORKSPACE}:${WORKSPACE}:rw \
                            --workdir ${WORKSPACE} \
                            --user `id -u`:`id -g` \
                            armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:latest \
                            kubectl -n ${NAMESPACE} --kubeconfig ./admin.conf delete jobs,pods -l 'jobTag=onboarding-jobs'
                        """

                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Remove Installed PVCs') {
            steps {
                script {
                    sh "${bob} remove-installed-pvcs"
                }
            }
        }
        stage('Removing Resources'){
            parallel{
                stage('Remove TLS Secrets') {
                    steps {
                        script {
                            sh "${bob} remove-tls-secrets"
                        }
                    }
                }
                stage('Remove Network Policies') {
                    steps {
                        script {
                            sh "${bob} remove-network-policies"
                        }
                    }
                }
                stage('Remove ClusterRoles & ClusterRoleBindings') {
                    steps {
                        script {
                            sh "${bob} remove-clusterroles"
                            sh "${bob} remove-cluster-rolebindings"
                        }
                    }
                }
            }
        }
        stage('Remove Storage Encryption Provider from Namespace') {
            steps {
                retry(count: 3){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Remove Storage Encryption Provider from Namespace\" stage. Retry ${RETRY_ATTEMPT} of 3. Sleeping 20 seconds before retry..."
                            sleep(20)
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} remove-eric-storage-encryption-provider-release-from-namespace"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Remove Namespace') {
            steps {
                script {
                    sh "${bob} remove-namespace"
                }
            }
        }
        stage('Full Clean Down on the environment - Removing CRD Components') {
            when {
                expression { params.CLEANUP_TYPE == "FULL" }
            }
            steps {
                script {
                    sh "${bob} remove-all-crd-helm-releases-from-namespace"
                    sh "${bob} remove-all-crd-components"
                    sh "${bob} remove-crd-namespace"
                }
            }
        }
    }
    post {
        always {
            script {
                sh "${bob} gather-logs:gather-system-logs || true"
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                    archiveArtifacts artifacts: "**/system_logs_*.tgz", allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        failure {
            script {
                sh "${bob} gather-logs:gather-system-logs || true"
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