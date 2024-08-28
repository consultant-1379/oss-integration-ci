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
        string(name: 'ARMDOCKER_USER_SECRET',
                description: 'ARM Docker secret.')
        string( name: 'GERRIT_REFSPEC',
                description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
        string( name: 'CHART_NAME',
                description: 'Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg.')
        string( name: 'CHART_VERSION',
                description: 'Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57.')
        string( name: 'CHART_REPO',
                description: 'Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2.')
        string( name: 'GIT_REPO_URL',
                description: ' gerrit https url to helm chart git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart.')
        string( name: 'CHART_PATH',
                description: 'Relative path to chart.yaml or the helmfile.yaml in git repo.')
        string( name: 'HELM_INTERNAL_REPO',
                description: 'Internal Helm chart repository url.')
        string( name: 'HELM_DROP_REPO',
                description: 'Drop Helm chart repository url.')
        string( name: 'HELM_REPO_CREDENTIALS_ID',
                description: 'Repositories.yaml file credential used for auth.')
        string( name: 'SPINNAKER_PIPELINE_ID',
                defaultValue: '123456',
                description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
        string( name: 'VCS_BRANCH',
                defaultValue: 'master',
                description: 'Branch for the change to be pushed.')
        string( name: 'STATE_VALUES_FILE',
                defaultValue: 'None',
                description: 'Site values file that is used for the helmfile build, this pre-populated file can be found in the oss-integration-ci repo')
        string( name: 'CI_HELM',
                defaultValue: 'true',
                description: 'If set to true, the ci-helm command will be used to package the helm chart.')
        string( name: 'ALLOW_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, downgrade of dependency is allowed.')
        string( name: 'VERSION_CHECK_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).')
        string( name: 'IGNORE_NON_RELEASED',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, wont upload helm chart to drop or release repo if CHART_VERSION is non-released (e.g. 1.0.0-11).')
        string( name: 'AUTOMATIC_RELEASE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, publish integration helm chart to released repo if all dependencies are released.')
        string( name: 'ALWAYS_RELEASE',
                defaultValue: 'true',
                description: 'Default is \'true\', if set to true, Always upload to released repo with released version, AUTOMATIC_RELEASE is ignored if this is set to true.')
        choice( name: 'VERSION_STEP_STRATEGY_DEPENDENCY',
                choices: "MINOR\nPATCH\nMAJOR",
                description: 'Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when dependency change received. Default is MINOR.')
        choice( name: 'VERSION_STEP_STRATEGY_MANUAL',
                choices: "MINOR\nPATCH\nMAJOR",
                description: 'Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when manual change received. Default is MINOR.')
        string(name: 'GERRIT_PREPARE_OR_PUBLISH',
                defaultValue: 'prepare',
                description: 'prepare :: Prepare Integration Helm Chart and uploads to the snapshot/internal repo. publish :: Checks in the updates to git and upload to the drop repo. prep :: Builds a local copy of the snapshot tar file.')
        string( name: 'CHECK_PUBLISHED',
                defaultValue: 'true',
                description: 'If set to true, and the parameter GERRIT_PREPARE_OR_PUBLISH is set to "publish", the console output will be checked to ensure a new helm chart has been uploaded. If a new chart was not created the job will fail. Used for Helm charts only.')
        string( name: 'COMMIT_MESSAGE_FORMAT_MANUAL',
                defaultValue: '%ORIGINAL_TITLE (%INT_CHART_VERSION)',
                description: 'User defined manual git commit message format string template.')
        string( name: 'GIT_TAG_ENABLED',
                defaultValue: 'true',
                description: 'Create a tag for the git commit, default is false.')
        string( name: 'WAIT_SUBMITTABLE_BEFORE_PUBLISH',
                defaultValue: 'true',
                description: 'For the publish command, wait for the gerrit patch to be set for a verified +1 or +2 or both before submitting, default is true.')
        string( name: 'WAIT_TIMEOUT_SEC_BEFORE_PUBLISH',
                defaultValue: '120',
                description: 'Timeout in seconds wait for a verifed +1 or +2 or both before submitting. Default is 120s.')
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
        HELM_REPO_CREDENTIALS = "${env.WORKSPACE}/arm_repositories.yaml"
        HELM_UPLOAD_REPO = "${params.HELM_INTERNAL_REPO}"
        HELM_RELEASED_REPO = "${params.HELM_DROP_REPO}"
        STATE_VALUES_FILE = "${env.WORKSPACE}/${params.STATE_VALUES_FILE}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker_configs"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${GERRIT_PREPARE_OR_PUBLISH} ${CHART_NAME} ${GERRIT_REFSPEC}"
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
        stage('Install Docker Config') {
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                    }
                }
            }
        }
        stage('Package') {
            steps {
                script {
                    retry(3) {
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE'), string(credentialsId: 'eo-helm-repo-api-token', variable: 'ARM_API_TOKEN')]) {
                            sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${env.HELM_REPO_CREDENTIALS}"
                            sh 'rm -rf .bob/tmp_repo'
                            // EIC FBU specific functionality
                            if (params.GIT_REPO_URL.contains('eiae-helmfile'))
                            {
                                try {
                                    sh "${bob} adp-inca-enabler:fetch-build-upload > submit-helmfile-output.txt"
                                    sh 'echo "BUILD_STATUS=SUCCESS" >> artifact.properties'
                                } catch (Exception e) {
                                    if (env.GERRIT_PREPARE_OR_PUBLISH == "publish") {
                                        error_output = sh(script: "cat submit-helmfile-output.txt", returnStdout: true).trim()
                                        if (error_output.contains("Downgrade is not allowed!")) {
                                            echo "A downgrade error occurred - this is being recorded in the artifact.properties file"
                                            sh 'echo "BUILD_STATUS=DOWNGRADE_NOT_ALLOWED" >> artifact.properties'
                                            currentBuild.result = 'FAILURE'
                                            return
                                        }
                                    }
                                    throw Exception
                                } finally {
                                    echo "The output from the ${env.GERRIT_PREPARE_OR_PUBLISH} command:"
                                    sh "cat submit-helmfile-output.txt"
                                }
                            }
                            else if (params.GIT_REPO_URL.contains('eo-helmfile') && (env.GERRIT_PREPARE_OR_PUBLISH == "prep"))
                            {
                                sh "${bob} adp-inca-enabler:fetch-build-upload"
                                sh 'echo "BUILD_STATUS=SUCCESS" >> artifact.properties'
                            }
                            else
                            {
                                sh "${bob} adp-inca-enabler:fetch-build-upload"
                            }
                        }
                    }
                }
            }
        }
        stage('Check if new package released by publish') {
            when {
                allOf {
                    expression { params.GERRIT_PREPARE_OR_PUBLISH == "publish" }
                    expression { params.CHECK_PUBLISHED == "true" }
                }
            }
            steps {
                script {
                    if (currentBuild.rawBuild.getLog().contains('There is no change, not uploading new helm chart.Probably publish was triggered with same change')) {
                        error("Build failed because chart publish job was retriggered with the same parameters and no new chart released.")
                        // Requested in jira SM-106379
                    }
                }
            }
        }
        stage('Build Python-CI Scripts Image') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" && params.GIT_REPO_URL.contains('eo-helmfile')}
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
            }
        }
        stage('Gather Site Values File') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" && params.GIT_REPO_URL.contains('eo-helmfile')}
            }
            environment {
                FULL_PATH_TO_SITE_VALUES_FILE="${env.WORKSPACE}/site-values/eo/ci/template/site-values-latest.yaml"
                FULL_PATH_TO_HELMFILE_TEMPLATE_OVERRIDE_FILE="${env.WORKSPACE}/.bob/tmp_repo/testsuite/helm-chart-validator/site_values.yaml"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                      if (params.GIT_REPO_URL.contains('eo-helmfile'))
                      {
                        sh "${bob} run-helmfile-validator:gather-site-values-file"
                      }
                    }
                }
            }
        }
        stage('Generate Optionality File') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" && params.GIT_REPO_URL.contains('eo-helmfile')}
            }
            environment {
                HELMFILE_PATH_FOR_OPTIONALITY="${env.WORKSPACE}/.bob/tmp_repo/helmfile"
                PATH_FOR_OPTIMIZED_FILE="${env.WORKSPACE}/.bob/tmp_repo/helmfile_optimized"
                STATE_VALUES_FILE="${env.WORKSPACE}/site_values.yaml"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                      if (params.GIT_REPO_URL.contains('eo-helmfile'))
                      {
                        sh "${bob} generate-optionality-maximum"
                      }
                    }
                }
            }
        }
        stage('Run Precode Testing'){
            parallel{
                stage('Run EO Helmfile Validator') {
                    when {
                        expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" && params.GIT_REPO_URL.contains('eo-helmfile') }
                    }
                    environment {
                        PATH_FOR_OPTIMIZED_FILE="${env.WORKSPACE}/.bob/tmp_repo/helmfile_optimized"
                        HELMFILE_VALIDATOR_DIRECTORY_PATH = "testsuite/common/helmfile-validator"
                        COMMON_SKIP_LIST_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/common_skip_list.json"
                        SPECIFIC_SKIP_LIST_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/eo-helmfile/skip_list.json"
                        STATE_VALUES_FILE="${env.WORKSPACE}/site_values.yaml"
                        CHECK_SPECIFIC_CONTENT_FILE_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/eo-helmfile/check_specific_content.json"
                    }
                    steps {
                        script {
                            withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                                sh "${bob} run-helmfile-validator:helmfile-validator"
                            }
                        }
                    }
                    post {
                        always {
                            sh "mv report.html helmfile-validator-test-report.html"
                            archiveArtifacts artifacts: 'helmfile-validator-test-report.html', allowEmptyArchive: true
                        }
                    }
                }
                stage('Kubernetes Range Compatibility Tests') {
                    when {
                        expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" && params.GIT_REPO_URL.contains('eo-helmfile')}
                    }
                    environment {
                        KUBE_VERSION_FILE_PATH="${env.WORKSPACE}/.bob/eric-eo-helmfile_tmp/eric-eo-helmfile/kubeVersion.yaml"
                        SITE_VALUES_FILE_PATH_FOR_KUBERNETES_COMPATIBILITY_CHECKS="${WORKSPACE}/.bob/tmp_repo/ci/jenkins/site-values/k8s-compatibility-site-values.yaml"
                        HELMFILE_OR_HELM_CHART_FILE_PATH="${env.WORKSPACE}/.bob/eric-eo-helmfile_tmp/eric-eo-helmfile/helmfile.yaml"
                        KUBEVAL_KINDS_TO_SKIP="HTTPProxy,CertificateAuthority,ClientCertificate,InternalCertificate,InternalUserCA,ServerCertificate,CustomResourceDefinition,DestinationRule,EnvoyFilter,PeerAuthentication,Gateway,Sidecar,Telemetry,template,VirtualService,CassandraCluster,Kafka,KafkaBridge,ExternalCertificate"
                    }
                    steps {
                        script {
                            withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                                sh "${bob} run-kubernetes-compatibility-tests"
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {

                    sh 'echo "TYPE_DEPLOYMENT=${GERRIT_PREPARE_OR_PUBLISH}" >> artifact.properties'
                    archiveArtifacts allowEmptyArchive: true, artifacts: "artifact.properties", fingerprint: true
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
