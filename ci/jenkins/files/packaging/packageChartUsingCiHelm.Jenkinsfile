#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string(name: 'GERRIT_REFSPEC',
              description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
        string(name: 'CHART_NAME',
              description: 'Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg')
        string(name: 'CHART_VERSION',
              description: 'Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57')
        string(name: 'CHART_REPO',
              description: 'Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2')
        string(name: 'GIT_REPO_URL',
              description: 'gerrit https url to helm chart git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart')
        string(name: 'GERRIT_PROJECT',
              description: 'Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base')
        string(name: 'HELM_INTERNAL_REPO',
              defaultValue: "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm-local",
              description: 'Repository to upload the snapshot version to')
        string(name: 'VCS_BRANCH',
              defaultValue: 'master',
              description: 'Branch for the change to be pushed')
        string(name: 'CHART_PATH',
                description: 'Relative path to helm chart in git repo.')
        string(name: 'USE_DEPENDENCY_CACHE',
              defaultValue: 'false',
              description: 'If set to true, it uses the dependency cache directory within /tmp/cachedir to push and pull dependency from')
        string(name: 'DEPENDENCY_CACHE_DIRECTORY',
              defaultValue: '/tmp/cachedir',
              description: 'Specify the cache directory on the Jenkins Agent to push and pull dependencies from')
        string( name: 'ALLOW_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, downgrade of dependency is allowed.')
        string(name: 'VERSION_CHECK_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).')
        string(name: 'GERRIT_USER_SECRET',
              description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARTIFACT_UPLOAD_TO_ARM',
              defaultValue: 'true',
              description: 'If set to true, will upload the artifact to the specified ARM repository, else it will be attached to the jenkins job as an artifact for local testing.')
        string(name: 'ARMDOCKER_USER_SECRET',
              description: 'Jenkins secret ID with ARM Docker config details')
        string(name: 'HELM_REPO_CREDENTIALS_ID',,
              description: 'Repositories.yaml file credential used for auth')
        string(name: 'FUNCTIONAL_USER_TOKEN',
              description: 'Jenkins secret token ID for ARM Registry Token.')
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
        string(name: 'CI_REFSPEC',
              defaultValue: 'refs/heads/master',
              description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    agent {
        label env.SLAVE_LABEL
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        HELM_REPO_CREDENTIALS = "${env.WORKSPACE}/repositories.yaml"
        VERSION_STEP_STRATEGY_DEPENDENCY = "PATCH"
        VERSION_STEP_STRATEGY_MANUAL = "PATCH"
        COMMIT_MESSAGE_FORMAT_MANUAL = '%ORIGINAL_TITLE (%INT_CHART_VERSION)'
        HELM_DROP_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
        HELM_RELEASED_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
        CHART_PATH = ".bob/cloned_repo/${env.CHART_PATH}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker_configs"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${CHART_PATH.split("/")[-1]}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                    }
                    if (env.CI_DOCKER_IMAGE == "local") {
                        sh "${bobInternal} build-local-python-ci-image"
                    }
                }
            }
        }
        stage('Fetch Chart Repo') {
            environment {
                ARTIFACT_PATH = "${env.CHART_PATH}"
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Fetch Chart Repo\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                            sh "rm -rf .bob/cloned_repo"
                        }
                        else {
                            echo "Running the \"Fetch Chart Repo\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bobInternal} gerrit:clone-repo-restricted"
                            if (env.GERRIT_REFSPEC != "") {
                                sh "${bobInternal} gerrit:checkout-patch"
                            }
                            else {
                                sh "${bob} adp-inca-enabler:set-allow-downgrade-parameter"
                                sh "${bob} adp-inca-enabler:update-version"
                            }
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Set Dev Chart Version') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Set Dev Chart Version\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Set Dev Chart Version\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} helm-chart-management:get-current-chart-version"
                        sh "${bobInternal} gerrit:get-next-dev-version"
                        sh "${bob} helm-chart-management:set-unique-dev-version helm-chart-management:get-git-head-sha"
                        sh "${bob} helm-chart-management:set-time"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Package') {
            environment {
                TEST_CHART_VERSION = get_dev_version("${params.GERRIT_REFSPEC}")
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"ADP CIHELM - Package\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"ADP CIHELM - Package\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bob} dependency-cache-management:make-cache-dir helm-chart-management:package-chart helm-chart-management:get-chart-name"

                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Upload to ARM') {
            when {
                environment ignoreCase:true, name: 'ARTIFACT_UPLOAD_TO_ARM', value: 'true'
            }
            environment {
                ARTIFACT_NAME = get_chart_name()
                ARTIFACT_VERSION = get_dev_version("${params.GERRIT_REFSPEC}")
                HELM_REPO_NAME = "${env.HELM_INTERNAL_REPO}"
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Upload to ARM\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Upload to ARM\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([string(credentialsId: params.FUNCTIONAL_USER_TOKEN, variable: 'FUNCTIONAL_USER_TOKEN')]) {
                            sh "${bob} adp-inca-enabler:upload-to-arm adp-inca-enabler:generate-artifact"
                        }
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
                    archiveArtifacts artifacts: 'artifact.properties, *.tgz', allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        failure {
            script {
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                    archiveArtifacts artifacts: "*.tgz, ci-script-executor-logs/*", allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
}

def get_chart_name() {
    String int_chart_name = readFile ".bob/var.int-chart-name"
    String trimmed_int_chart_name = int_chart_name.trim()
    return trimmed_int_chart_name
}

def get_dev_version(refspec) {
    String dev_version = readFile ".bob/var.next-version-prefix"
    String git_sha = readFile ".bob/var.git-head-sha"
    String trimmed_dev_version = dev_version.trim()
    String trimmed_git_sha = git_sha.trim()
    String time = readFile ".bob/var.time-stamp"
    String trimmed_time = time.trim()
    if (!refspec.isEmpty()) {
      return trimmed_dev_version + trimmed_git_sha
    }
    return trimmed_dev_version + trimmed_time
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
