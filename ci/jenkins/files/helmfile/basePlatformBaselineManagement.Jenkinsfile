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
    parameters {
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
        string(name: 'GERRIT_BRANCH',
              defaultValue: 'master',
              description: 'Gerrit branch the review should be submitted to, default: master')
        string(name: 'HELM_INTERNAL_REPO',
              description: 'Repository to upload the snapshot version to.')
        string(name: 'HELM_DROP_REPO',
               description: 'Repository to upload the released version to.')
        string(name: 'HELMFILE_PATH',
              description: 'Relative path to helm chart in git repo.')
        string( name: 'STATE_VALUES_FILE',
                defaultValue: 'None',
                description: 'Site values file that is used for the helmfile build, this pre-populated file can be found in the oss-integration-ci repo')
        string(name: 'VERSION_CHECK_DOWNGRADE',
              defaultValue: 'false',
              description: 'Default is \'false\', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).')
        string(name: 'ALLOW_DOWNGRADE',
              defaultValue: 'false',
              description: 'Default is \'false\', if set to true, downgrade of dependency is allowed.')
        string(name: 'VERSION_STEP_STRATEGY_MANUAL',
              defaultValue: 'MINOR',
              description: 'Possible values: MAJOR, MINOR, PATCH. Step the version in metadata.yaml when dependency change received. Default is MINOR.')
        string(name: 'GERRIT_USER_SECRET',
              description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'GERRIT_PREPARE_OR_PUBLISH',
              defaultValue: 'prepare',
              description: 'prepare :: Prepare Helmfile and uploads to the snapshot/internal repo. publish :: Checks in the updates to git and upload to the drop repo')
        string(name: 'ARTIFACT_UPLOAD_TO_ARM',
               defaultValue: 'true',
               description: 'If set to true, will upload the artifact to the specified ARM repository, else it will be attached to the jenkins job as an artifact for local testing. ARTIFACT_UPLOAD_TO_ARM takes presidence over GERRIT_PREPARE_OR_PUBLISH')
        string(name: 'SPINNAKER_PIPELINE_ID',
              defaultValue: '123456',
              description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string(name: 'ARMDOCKER_USER_SECRET',
              description: 'Jenkins secret ID with ARM Docker config details')
        string(name: 'FUNCTIONAL_USER_TOKEN',
              description: 'Jenkins secret token ID for ARM Registry Token.')
        string(name: 'WAIT_SUBMITTABLE_BEFORE_PUBLISH',
              defaultValue: 'false',
              description: 'For the publish command, wait for the gerrit patch to be set for a verified +1 or +2 or both before submitting, default is false.')
        string(name: 'WAIT_TIMEOUT_SEC_BEFORE_PUBLISH',
              defaultValue: '120',
              description: 'Timeout in seconds wait for a verifed +1 or +2 or both before submitting. Default is 120s.')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'Number of seconds before the submodule update command times out')
        string(name: 'AGENT_LABEL',
               defaultValue: 'evo_docker_engine',
               description: 'Specify the Jenkins agent label that you want the job to run on')
        string(name: 'CI_DOCKER_IMAGE',
              defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
              description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'CI_REFSPEC',
              defaultValue: 'refs/heads/master',
              description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    agent {
        label env.AGENT_LABEL
    }
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
        disableConcurrentBuilds()
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        HELM_REPO_CREDENTIALS = "${env.WORKSPACE}/repositories.yaml"
        HELM_REPO_NAME = set_upload_repo("${params.GERRIT_PREPARE_OR_PUBLISH}", "${params.HELM_DROP_REPO}", "${params.HELM_INTERNAL_REPO}")
        HELMFILE_PATH = ".bob/cloned_repo/${env.HELMFILE_PATH}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker_configs"
        VCS_BRANCH = "${params.GERRIT_BRANCH}"
        ADD_NEW_REPO_DETAILS = set_repo_update("${params.GERRIT_PREPARE_OR_PUBLISH}")
        SKIP_HELMFILE_REPO_UPDATE = set_skip_repo_update("${params.GERRIT_PREPARE_OR_PUBLISH}")
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${HELMFILE_PATH.split("/")[-1]} (${params.GERRIT_PREPARE_OR_PUBLISH})"
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
        stage('Fetch Helmfile Repo') {
            environment {
                ARTIFACT_PATH = "${env.HELMFILE_PATH}"
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Fetch Helmfile Repo\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                            sh "rm -rf .bob/cloned_repo"
                        }
                        else {
                            echo "Running the \"Fetch Helmfile Repo\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bobInternal} gerrit:clone-repo-restricted"
                            sh "${bob} adp-inca-enabler:update-helmfile-version"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Get Current Helmfile details') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Get Current Helmfile details\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Get Current Helmfile details\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} helmfile-details:get-current-helmfile-version helmfile-details:get-current-helmfile-name"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Get Next Helmfile Version') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Get Next Helmfile Version\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Get Next Helmfile Version\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        if (env.GERRIT_PREPARE_OR_PUBLISH == "publish") {
                            sh "${bob} gerrit:get-next-release-version"
                        }
                        else {
                            sh "${bob} helm-chart-management:set-time gerrit:get-next-dev-version gerrit:set-unique-version-using-timestamp"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Package') {
            environment {
                ARTIFACT_NAME = get_name()
                ARTIFACT_VERSION = get_version()
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Package\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Package\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bob} helmfile-details:step-helmfile-metadata"
                            sh "${bob} helmfile-management:package-helmfile"
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
                ARTIFACT_NAME = get_name()
                ARTIFACT_VERSION = get_version()
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
                            sh "${bob} adp-inca-enabler:upload-to-arm"
                            sh '''
                                echo "BASE_PLATFORM_BASELINE_NAME=${ARTIFACT_NAME}" >> artifact.properties
                                echo "BASE_PLATFORM_BASELINE_VERSION=${ARTIFACT_VERSION}" >> artifact.properties
                                echo "BASE_PLATFORM_BASELINE_REPO=${HELM_REPO_NAME}" >> artifact.properties
                            '''
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Create Review') {
            when {
                allOf {
                    environment ignoreCase:true, name: 'GERRIT_PREPARE_OR_PUBLISH', value: 'publish'
                    environment ignoreCase:true, name: 'ARTIFACT_UPLOAD_TO_ARM', value: 'true'
                }
            }
            environment {
                ARTIFACT_VERSION = get_version()
                COMMIT_MESSAGE_FORMAT_MANUAL = "[${env.ARTIFACT_VERSION}] Updated ${params.CHART_NAME} with ${params.CHART_VERSION}"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} gerrit:create-patch"
                    }
                }
            }
        }
        stage('Check Review') {
            when {
                allOf {
                    environment ignoreCase:true, name: 'GERRIT_PREPARE_OR_PUBLISH', value: 'publish'
                    environment ignoreCase:true, name: 'ARTIFACT_UPLOAD_TO_ARM', value: 'true'
                }
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Check Review\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Check Review\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            withEnv(readFile('gerrit_create_patch.properties').split('\n') as List) {
                                sh "${bob} gerrit:set-review-labels gerrit:review-change gerrit:check-code-submittable"
                            }
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Submit Review') {
            when {
                allOf {
                    environment ignoreCase:true, name: 'GERRIT_PREPARE_OR_PUBLISH', value: 'publish'
                    environment ignoreCase:true, name: 'ARTIFACT_UPLOAD_TO_ARM', value: 'true'
                }
            }
            environment {
                ARTIFACT_VERSION = get_version()
                COMMIT_MESSAGE_FORMAT_MANUAL = "[${env.ARTIFACT_VERSION}] Updated ${params.CHART_NAME} with ${params.CHART_VERSION}"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        withEnv(readFile('gerrit_create_patch.properties').split('\n') as List) {
                            sh "${bob} gerrit:submit-change"
                            sh '''
                                echo 'COMMIT_MESSAGE="'${COMMIT_MESSAGE_FORMAT_MANUAL}'"' >> artifact.properties
                                echo "COMMIT_REVIEW_URL=\"${GERRIT_URL}\"" >> artifact.properties
                            '''
                        }
                    }
                }
            }
        }
        stage('Tag Submission to Gerrit') {
            when {
                allOf {
                    environment ignoreCase:true, name: 'GERRIT_PREPARE_OR_PUBLISH', value: 'publish'
                    environment ignoreCase:true, name: 'ARTIFACT_UPLOAD_TO_ARM', value: 'true'
                }
            }
            environment {
                ARTIFACT_VERSION = get_version()
                COMMIT_MESSAGE_FORMAT_MANUAL = "[${env.ARTIFACT_VERSION}] Updated ${params.CHART_NAME} with ${params.CHART_VERSION}"
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Tag Submission to Gerrit\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Tag Submission to Gerrit\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            withEnv(readFile('gerrit_create_patch.properties').split('\n') as List) {
                                sh "${bob} gerrit:git-tag"
                            }
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

def get_name() {
    String name = readFile ".bob/var.helmfile-name"
    String trimmed_name = name.trim()
    return trimmed_name
}

def get_version() {
      String version = readFile ".bob/var.next-version-prefix"
      String trimmed_version = version.trim()
      return trimmed_version
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

def set_upload_repo(gerrit_prepare_or_publish, drop_repo, internal_repo) {
    if (gerrit_prepare_or_publish.contains("publish")) {
        return drop_repo
    }
    else {
        return internal_repo
    }
}

def set_repo_update(gerrit_prepare_or_publish) {
    if (gerrit_prepare_or_publish.contains("prepare")) {
        return true
    }
    else {
        return false
    }
}

def set_skip_repo_update(gerrit_prepare_or_publish) {
    if (gerrit_prepare_or_publish.contains("prepare")) {
        return false
    }
    else {
        return true
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
