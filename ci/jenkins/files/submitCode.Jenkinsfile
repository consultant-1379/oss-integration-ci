#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bob_k8s_checks = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/common/ruleset_kubernetes_range_checks.yaml"
def DR_PARAMETERS = ''

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'eoadm100-user-credentials',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'eoadm100-docker-auth-config',
                description: 'ARM Docker secret')
        string( name: 'GERRIT_REFSPEC',
                description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
        string( name: 'CHART_NAME',
                description: 'Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg')
        string( name: 'CHART_VERSION',
                description: 'Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57')
        string( name: 'CHART_REPO',
                description: 'Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2')
        string( name: 'GIT_REPO_URL',
                defaultValue: 'https://gerrit-gamma.gic.ericsson.se/a/OSS/com.ericsson.oss.aeonic/oss_integration_charts.git',
                description: 'gerrit https url to helm chart git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart')
        string( name: 'VCS_BRANCH',
                defaultValue: 'master',
                description: 'Branch for the change to be pushed')
        string( name: 'CHART_PATH',
                defaultValue: 'charts/eric-oss',
                description: 'Relative path to helm chart in git repo.')
        string( name: 'HELM_INTERNAL_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm',
                description: 'Internal Helm chart repository url.')
        string( name: 'HELM_DROP_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
                description: 'Drop Helm chart repository url.')
        string( name: 'HELM_RELEASED_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-released-helm-perm',
                description: 'Released Helm chart repository url.')
        string( name: 'HELM_REPO_CREDENTIALS_ID',
                defaultValue: 'eoadm100_helm_repository_creds',
                description: 'Repositories.yaml file credential used for auth')
        string(name: 'HELM_REPO_API_TOKEN',
                defaultValue: 'eo-helm-repo-api-token',
                description: 'token to access Helm repository')
        string( name: 'ALLOW_DOWNGRADE',
                defaultValue: 'true',
                description: 'Default is \'false\', if set to true, downgrade of dependency is allowed.')
        string( name: 'VERSION_CHECK_DOWNGRADE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).')
        string( name: 'IGNORE_NON_RELEASED',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, wont upload helm chart to drop or release repo if CHART_VERSION is non-released (e.g. 1.0.0-11).')
        string( name: 'AUTOMATIC_RELEASE',
                defaultValue: 'true',
                description: 'Default is \'true\', if set to true, publish integration helm chart to released repo if all dependencies are released.')
        string( name: 'ALWAYS_RELEASE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, Always use upload to released repo with released version.')
        string( name: 'PLUS_RELEASE_MODE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, the release version is calculated following the plus release mode.')
        choice( name: 'VERSION_STEP_STRATEGY_DEPENDENCY',
                choices: "PATCH\nMINOR\nMAJOR",
                description: 'Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when dependency change received. Default is PATCH')
        choice( name: 'VERSION_STEP_STRATEGY_MANUAL',
                choices: "PATCH\nMINOR\nMAJOR",
                description: 'Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when manaul change received. Default is MINOR')
        choice( name: 'GERRIT_PREPARE_OR_PUBLISH',
                choices: "prepare\npublish\nprepare-dev\nprep\n",
                description: '''prepare-dev :: Prepare Integration Helm Chart for development\n
                                prepare :: Prepare Integration Helm Chart\n
                                publish :: Publish Integration Helm Chart\n
                                publish :: Checks in the updates to git and upload to the release repo\n
                                prep :: Builds a local copy of the snapshot tar file and executes the precode tests against the updated chart''')
        string( name: 'COMMIT_MESSAGE_FORMAT_MANUAL',
                defaultValue: '%ORIGINAL_TITLE (%INT_CHART_VERSION)',
                description: 'User defined manual git commit message format string template')
        string( name: 'GIT_TAG_ENABLED',
                defaultValue: 'true',
                description: 'Create a tag for the git commit, default is false')
        string( name: 'WAIT_SUBMITTABLE_BEFORE_PUBLISH',
                defaultValue: 'true',
                description: 'For the publish command, wait for the gerrit patch to be set for a verified +1 or +2 or both before submitting, default is false')
        string( name: 'WAIT_TIMEOUT_SEC_BEFORE_PUBLISH',
                defaultValue: '120',
                description: 'Timeout in seconds wait for a verifed +1 or +2 or both before submitting. Default is 120s.')
        string( name: 'DESIGN_RULE_OPTIONS',
                defaultValue: '',
                description: '''This field allows to pass additional options that may be required for a particular application (e.g. to skip some tests), separated by space.\n
                              More details on possible options: https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/adp-cicd/adp-helm-dr-checker'.\n
                              Example: -DhelmDesignRule.config.DR-D1123-121=skip -DhelmDesignRule.config.DR-D1123-122=skip''')
        string(name: 'APP_NAME',
                defaultValue: 'eo',
                description: 'application name in repo')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'FORCE_VERSION_UPDATE',
                defaultValue: 'False',
                description: 'Default value is False. If there is no change in the requirements.yaml and setting this to True, will force the version to be stepped.')
        string(name: 'CI_HELM',
                defaultValue: 'true',
                description: 'If set to true, use ci-helm command to package helm chart. InCA uses the --netrc argument from cihelm which means that users might have to migrate to using the HELM_REPO_CREDENTIALS env variable.')
        string(name: 'KUBEVAL_KINDS_TO_SKIP',
                defaultValue: 'HTTPProxy,ServerCertificate,InternalCertificate,ClientCertificate,CertificateAuthority,adapter,attributemanifest,AuthorizationPolicy,CassandraCluster,CustomResourceDefinition,DestinationRule,EnvoyFilter,Gateway,handler,HTTPAPISpec,HTTPAPISpecBinding,instance,PeerAuthentication,QuotaSpec,QuotaSpecBinding,RbacConfig,RequestAuthentication,rule,ServiceEntry,ServiceRole,ServiceRoleBinding,Sidecar,Telemetry,template,VirtualService,WorkloadEntry,WorkloadGroup,Kafka,KafkaBridge',
                description: 'Those comma separated K8S resources will be passed to kubeval.sh script as skipped kinds.')
        string(name: 'FULL_CHART_SCAN',
                defaultValue: 'false',
                description: 'If "true" then with whole chart with its dependencies will be scanned in "prep"')
        string(name: 'TEST_OPENSHIFT',
                defaultValue: 'false',
                description: 'If "true" then Openshift tests will be ran on prepare.')
        string(name: 'DEBUG',
                defaultValue: 'false',
                description: 'Verbose git commands output for inca')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'Number of seconds before the submodule update command times out')
        string( name: 'CI_JOB_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    agent {
        label env.SLAVE_LABEL
    }
    environment {
        HELM_REPO_CREDENTIALS = "${env.WORKSPACE}/repositories.yaml"
        UPLOAD_INTERNAL = false
        HELM_UPLOAD_REPO = "${params.HELM_INTERNAL_REPO}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
        DEBUG_FLAG = prepare_debug_flag()
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${GERRIT_PREPARE_OR_PUBLISH} ${CHART_PATH.split("/")[-1]}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob oss-common-ci')
                sh "${bob} git-clean"
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
        stage('Prep helm chart') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE'), string(credentialsId: 'eo-helm-repo-api-token', variable: 'ARM_API_TOKEN')]) {
                        sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${env.HELM_REPO_CREDENTIALS}"
                        sh "${bob} review-publish-submit-chart"
                        env.DESIGN_RULE_OPTIONS = sh(script:'cat ${WORKSPACE}/.bob/tmp_repo/testsuite/design_rule_options.txt | tr "\n" " "', returnStdout: true).trim()
                        sh "echo DEBUG: env.DESIGN_RULE_OPTIONS , ${DESIGN_RULE_OPTIONS}"
                    }
                }
            }
        }
        stage('Copy Helm Template to Workspace Base Dir'){
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" }
            }
            steps {
                sh "${bob} copy-helm-template-to-base-dir"
            }
        }
        stage('Validate Helm3 Chart Schema') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" }
            }
            steps{
                    sh "${bob} validate-helm3-charts"
            }
        }
        stage('Build Helm Chart Validator Testsuite Image') {
            when {
                expression { params.TEST_OPENSHIFT == 'true' && params.GERRIT_PREPARE_OR_PUBLISH == "prep"}
            }
            steps {
                sh "${bob} build-helm-chart-validator-testsuite-image"
            }
        }
        stage('Run Openshift Static Tests') {
            when {
                expression { params.TEST_OPENSHIFT == 'true' && params.GERRIT_PREPARE_OR_PUBLISH == "prep"}
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} run-helm-chart-validator-testsuite:run-testsuite"
                    }
                }
            }
            post {
                always {
                    sh "${bob} helm-chart-validator-testsuite-report-and-clean"
                    archiveArtifacts artifacts: 'helm-chart-validator-test-report.html', allowEmptyArchive: true
                }
            }
        }
        stage('Set Design Rules Check parameters appropriate for the flow'){
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" }
            }
            steps {
                script {
                    if ( params.FULL_CHART_SCAN.toLowerCase() == "true" ) {
                        // Parameters to test only triggered microservice dependency chart
                        def CHART_PACKAGE = findFiles(glob: "${env.APP_NAME}-*.tgz")
                        DR_PARAMETERS = "--helm-chart ${CHART_PACKAGE[0].path} " +
                                        "-DhelmDesignRule.feature.dependency=0 "
                    } else if (params.CHART_NAME) {
                        DR_PARAMETERS = "--helm-chart-repo ${params.CHART_REPO} " +
                                        "--helm-chart-name ${params.CHART_NAME} " +
                                        "--helm-chart-version ${params.CHART_VERSION} "
                    } else {
                        // Check only top level chart if job triggered from REFSPEC
                        def CHART_PACKAGE = findFiles(glob: "${env.APP_NAME}-*.tgz")
                        DR_PARAMETERS = "--helm-chart ${CHART_PACKAGE[0].path} " +
                                        "-DhelmDesignRule.feature.dependency=1 "
                    }
                    echo "DR_PARAMETERS: ${DR_PARAMETERS}"

                    // Put DR commands in front of provided in parameters DESIGN_RULE_OPTIONS
                    env.DESIGN_RULE_OPTIONS = DR_PARAMETERS + env.DESIGN_RULE_OPTIONS
                    echo "DESIGN_RULE_OPTIONS: ${DESIGN_RULE_OPTIONS}"
                }
            }
        }
        stage('Design Rules Check') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "prep" }
            }
            steps {
                withCredentials([file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE')]) {
                    sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${HELM_REPO_CREDENTIALS}"
                    sh "${bob} design-rule-checker"
                }
            }
            post {
                always {
                    archiveArtifacts 'design-rule-check-report.html'
                }
            }
        }
        stage('Package and release helm chart') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH != "prep" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE'), string(credentialsId: env.HELM_REPO_API_TOKEN, variable: 'ARM_API_TOKEN')]) {
                        sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${env.HELM_REPO_CREDENTIALS}"
                        sh "${bob} review-publish-submit-chart"
                        sh 'echo "TYPE_DEPLOYMENT=${GERRIT_PREPARE_OR_PUBLISH}" >> artifact.properties'
                        archiveArtifacts 'artifact.properties'
                    }
                }
            }
        }
        stage('Check if no new charts released by publish') {
            when {
                expression { params.GERRIT_PREPARE_OR_PUBLISH == "publish" }
            }
            steps {
                script {
                    if (currentBuild.rawBuild.getLog().contains('There is no change, not uploading new helm chart.Probably publish was triggered with same change')) {
                        error("Build failed because chart publish job was retriggered with the same parameters and no new chart released. Requested in jira SM-106379")
                    }
                }
            }
        }
    }
    post {
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

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}

def prepare_debug_flag() {
    echo 'Set gerrit debug variable'
    return params.DEBUG == 'true' ? '--env GIT_CURL_VERBOSE=1 --env GIT_TRACE=1' : ' '
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