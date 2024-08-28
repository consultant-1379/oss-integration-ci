#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string(name: 'GERRIT_USER_SECRET',
                description: 'Jenkins secret ID with Gerrit username and password.')
        string(name: 'FUNCTIONAL_USER_TOKEN',
              description: 'Jenkins secret token ID for ARM Registry Token.')
        string( name: 'GERRIT_REFSPEC',
                description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
        string( name: 'CHART_NAME',
                description: 'Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg.')
        string( name: 'CHART_VERSION',
                description: 'Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57.')
        string( name: 'CHART_REPO',
                description: 'Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2.')
        string(name: 'GERRIT_PROJECT',
              description: 'Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base')
        string( name: 'CHART_PATH',
                description: 'Relative path to chart.yaml or the helmfile.yaml in git repo.')
        string( name: 'HELM_INTERNAL_REPO',
                description: 'Internal Helm chart repository url.')
        string( name: 'SPINNAKER_PIPELINE_ID',
                defaultValue: '123456',
                description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string( name: 'VCS_BRANCH',
                defaultValue: 'master',
                description: 'Branch for the change to be pushed.')
        string( name: 'STATE_VALUES_FILE',
                defaultValue: 'None',
                description: 'Site values file that is used for the helmfile build, this pre-populated file can be found in the oss-integration-ci repo')
        string( name: 'ALLOW_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, downgrade of dependency is allowed.')
        string( name: 'VERSION_CHECK_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).')
        choice( name: 'VERSION_STEP_STRATEGY_MANUAL',
                choices: "MINOR\nPATCH\nMAJOR",
                description: 'Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when manual change received. Default is MINOR.')
        string(name: 'ARTIFACT_UPLOAD_TO_ARM',
               defaultValue: 'true',
               description: 'If set to true, will upload the artifact to the specified ARM repository, else it will be attached to the jenkins job as an artifact for local testing.')
        string( name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string( name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'Number of seconds before the submodule sync command times out')
        string( name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on.')
        string(name: 'CI_REFSPEC',
               defaultValue: 'refs/heads/master',
               description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    agent {
        label env.SLAVE_LABEL
    }
    environment {
        HELM_REPO_NAME = "${params.HELM_INTERNAL_REPO}"
        HELMFILE_PATH = ".bob/cloned_repo/${env.CHART_PATH}"
        STATE_VALUES_FILE = "${env.WORKSPACE}/${params.STATE_VALUES_FILE}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} prepare ${CHART_NAME} ${GERRIT_REFSPEC}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Cleaning Git Repo\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Cleaning Git Repo\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                        command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                        sh "${bob} git-clean"
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
                            if (env.GERRIT_REFSPEC != "") {
                                sh "${bobInternal} gerrit:checkout-patch"
                            }
                            else {
                                sh "${bob} check_helmfile_versions_against_given_versions:check_helmfile_versions_against_given_versions"
                                sh "${bob} adp-inca-enabler:update-helmfile-version"
                            }
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
                        sh "${bob} gerrit:get-commit-hash gerrit:get-next-dev-version gerrit:set-unique-version"
                        sh "${bob} helm-chart-management:set-time"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Step Helmfile Metadata') {
            environment {
                ARTIFACT_NAME = get_name()
                ARTIFACT_VERSION = get_snapshot_version()
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Step Helmfile Metadata\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Step Helmfile Metadata\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        sh "${bob} helmfile-details:step-helmfile-metadata"
                        sh "${bob} helmfile-management:rename-helmfile-basename"
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Package') {
            environment {
                ARTIFACT_NAME = get_name()
                HELMFILE_PATH = get_name()
                ARTIFACT_VERSION = get_snapshot_version()
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
                        sh "${bob} helmfile-management:package-helmfile"
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
                ARTIFACT_VERSION = get_snapshot_version()
                GERRIT_REFSPEC = "${params.GERRIT_REFSPEC}"
                CHART_NAME = "${params.CHART_NAME}"
                CHART_REPO = "${params.CHART_REPO}"
                CHART_VERSION = "${params.CHART_VERSION}"
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
                            sh "${bob} adp-inca-enabler:generate-artifact"
                        }
                        if (params.GERRIT_REFSPEC != "")
                        {
                            sh 'echo "GERRIT_REFSPEC=${GERRIT_REFSPEC}" >> artifact.properties'
                        }
                        else
                        {
                            sh '''
                                echo "CHART_NAME=${CHART_NAME}" >> artifact.properties
                                echo "CHART_REPO=${CHART_REPO}" >> artifact.properties
                                echo "CHART_VERSION=${CHART_VERSION}" >> artifact.properties
                            '''
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
                    if (params.GERRIT_REFSPEC == "") {
                        sh "${bob} check_helmfile_versions_against_given_versions:add-result-to-properties"
                    }
                    sh 'echo "TYPE_DEPLOYMENT=prepare" >> artifact.properties'
                    archiveArtifacts allowEmptyArchive: true, artifacts: "artifact.properties", fingerprint: true
                    if (params.ARTIFACT_UPLOAD_TO_ARM.toLowerCase() != 'true')
                    {
                        archiveArtifacts allowEmptyArchive: true, artifacts: "*.tgz", fingerprint: true
                    }
                }
            }
        }
        failure {
            script {
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
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

def get_snapshot_version() {
      String version = readFile ".bob/var.next-version-prefix"
      String trimmed_version = version.trim()
      String time = readFile ".bob/var.time-stamp"
      String trimmed_time = time.trim()
      return trimmed_version + trimmed_time
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
