#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */
def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bob_k8s_checks = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/common/ruleset_kubernetes_range_checks.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review \${GERRIT_PATCHSET_REVISION}"
def DR_PARAMETERS = ''
def RETRY_ATTEMPT_ADP_CIHELM = 1


pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string( name: 'GERRIT_REFSPEC',
                defaultValue: '',
                description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
        string( name: 'GERRIT_PATCHSET_REVISION',
                description: 'Revision string for the gerrit review. Example: Ieec3b0b65fcdf30872befa2e9ace06e96cd487b4.')
        string( name: 'CHART_NAME',
                description: 'Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg')
        string( name: 'CHART_VERSION',
                description: 'Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57')
        string( name: 'CHART_REPO',
                description: 'Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2')
        string( name: 'GIT_REPO_URL',
                description: 'gerrit https url to helm chart git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart')
        string( name: 'GERRIT_PROJECT',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base')
        string( name: 'VCS_BRANCH',
                defaultValue: 'master',
                description: 'Branch for the change to be pushed')
        string( name: 'CHART_PATH',
                description: 'Relative path to helm chart in git repo.')
        string( name: 'GERRIT_USER_SECRET',
                description: 'Jenkins secret ID with Gerrit username and password')
        string( name: 'ARMDOCKER_USER_SECRET',
                description: 'Jenkins secret ID with ARM Docker config details')
        string( name: 'HELM_REPO_CREDENTIALS_ID',
                description: 'Repositories.yaml file credential used for auth')
        string( name: 'APP_NAME',
                description: 'application name in repo')
        string( name: 'SCHEMA_TESTS_PATH',
                defaultValue: 'testsuite/schematests/tests',
                description: 'The path to the schema tests within the chart repo. Set to "NONE" to skip these tests')
        string( name: 'PATH_TO_SITE_VALUES_FILE',
                defaultValue: 'testsuite/site_values.yaml',
                description: 'The path including file name of the site values file for templating the chart for the static test and design rule checking. The path should start from the root of the App chart repo')
        string( name: 'FULL_CHART_SCAN',
                defaultValue: 'false',
                description: 'If "true" then with whole chart with its dependencies will be scanned in "prep"')
        string( name: 'USE_ADP_ENABLER',
                defaultValue: 'adp-cihelm',
                description: 'To use a specific adp enabler to build the chart, two options available, adp-cihelm or adp-inca. Default, adp-cihelm')
        string( name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string( name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'Number of seconds before the submodule sync command times out')
        string( name: 'SUBMODULE_UPDATE_TIMEOUT',
                defaultValue: '300',
                description: 'Number of seconds before the submodule update command times out')
        string( name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string( name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string( name: 'CI_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    agent {
        label env.SLAVE_LABEL
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        HELM_REPO_CREDENTIALS = "${env.WORKSPACE}/repositories.yaml"
        GERRIT_PREPARE_OR_PUBLISH = "prep"
        // Directory path to the helm-chart-validator
        HELM_CHART_VALIDATOR_DIRECTORY_PATH = "testsuite/common/helm-chart-validator"
        //Full path to the site values file including the bob tmp build directory.
        FULL_PATH_TO_SITE_VALUES_FILE = ".bob/cloned_repo/${params.PATH_TO_SITE_VALUES_FILE}"
        // Used to search the root of the HELM_CHART_VALIDATOR_DIRECTORY_PATH for all the schema files to iterate over
        SEARCH_STRING = "yaml"
        // Used to omit items found using the SEARCH_STRING, multiples can be added by adding a comma separated list, site_value,global,....,...'
        IGNORE_STRINGS = ""
        // PAth to the design rules
        DESIGN_RULES_PATH = "testsuite/common/adp_design_rule"
        // If set to true, downgrade of dependency is allowed.
        ALLOW_DOWNGRADE = "true"
        // If set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7)
        VERSION_CHECK_DOWNGRADE = "false"
        // If set to true, won't upload helm chart to drop or release repo if CHART_VERSION is non-released (e.g. 1.0.0-11).
        IGNORE_NON_RELEASED = "false"
        // If set to true, publish integration helm chart to released repo if all dependencies are released.
        AUTOMATIC_RELEASE = "true"
        // If set to true, Always upload to released repo with released version
        ALWAYS_RELEASE = "false"
        VERSION_STEP_STRATEGY_DEPENDENCY = "PATCH"
        VERSION_STEP_STRATEGY_MANUAL = "PATCH"
        COMMIT_MESSAGE_FORMAT_MANUAL = '%ORIGINAL_TITLE (%INT_CHART_VERSION)'
        HELM_INTERNAL_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm"
        HELM_DROP_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
        HELM_RELEASED_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
        TEST_CHART_VERSION = "0.0.0"
        CHART_PATH = ".bob/cloned_repo/${env.CHART_PATH}"

        FULL_PATH_TO_YAMLLINT_CONFIG_FILE = "/ci/jenkins/config/yamllint_config.yaml"
        TEMPLATE_OUTPUT_FILE_PATH = "${env.WORKSPACE}/yamllint_helm_template_output.yaml"
        YAMLLINT_OUTPUT_FILE_PATH = "${env.WORKSPACE}/yamllint_output.log"

        CI_HELM = "true"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
        IMAGE_INFORMATION_JSON_PATH = "${env.WORKSPACE}/image_information_list.json"
        IMAGE_INFORMATION_TEXT_PATH = "${env.WORKSPACE}/image_information_list.txt"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${CHART_PATH.split("/")[-1]}"
                }
            }
        }
        stage('Gerrit notification - build started') {
            when {
                expression { params.GERRIT_REFSPEC != '' }
            }
            steps {
                script {
                    sh "${gerritReviewCommand} --message '\"Build Started: ${BUILD_URL}\"'"
                }
            }
        }
        stage('Cleaning Git Repo') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
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
        stage('Build Python-CI Scripts Image') {
            when {
                environment ignoreCase: true, name: 'CI_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bobInternal} build-local-python-ci-image"
            }
        }
        stage('ADP INCA - Prep helm chart') {
            when {
                expression { params.USE_ADP_ENABLER != "adp-cihelm" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE'), string(credentialsId: 'eo-helm-repo-api-token', variable: 'ARM_API_TOKEN')]) {
                        sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${env.HELM_REPO_CREDENTIALS}"
                        sh "${bob} review-publish-submit-chart"
                        sh "${bob} copy-helm-template-to-base-dir"
                    }
                }
            }
        }
        stage('ADP CIHELM - Prep helm chart') {
            when {
                expression { params.USE_ADP_ENABLER == "adp-cihelm" }
            }
            environment {
                ARTIFACT_PATH = "${env.CHART_PATH}"
            }
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_ATTEMPT_ADP_CIHELM > 1) {
                            echo "Rerunning the \"ADP CIHELM - Prep helm chart\" stage. Retry ${RETRY_ATTEMPT_ADP_CIHELM} of 5. Sleeping before retry..."
                            sleep(60)
                            sh "rm -rf .bob/cloned_repo"
                        }
                        else {
                            echo "Running the \"ADP CIHELM - Prep helm chart\" stage. Try ${RETRY_ATTEMPT_ADP_CIHELM} of 5"
                        }
                        RETRY_ATTEMPT_ADP_CIHELM = RETRY_ATTEMPT_ADP_CIHELM + 1
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                            sh "${bobInternal} gerrit:clone-repo-restricted"
                            if (env.GERRIT_REFSPEC != "") {
                                sh "${bobInternal} gerrit:checkout-patch"
                            }
                            else {
                                sh "${bob} adp-inca-enabler:set-allow-downgrade-parameter"
                                sh "${bob} adp-inca-enabler:update-version"
                            }
                            if ( env.APP_NAME == "eric-oss-integration-chart-chassis" ) {
                                sh "${bob} edit-chassis-for-pcr"
                            }
                            sh "${bob} helm-chart-management:package-chart helm-chart-management:get-helm-chart-version"
                        }
                    }
                }
            }
        }
        stage('Un-zip Chart TGZ'){
            steps {
                script {
                    sh "${bob} unzip-app-chart"
                }
            }
        }
        stage('Run Precode Testing'){
            parallel{
                stage('Validating eric-product-info images'){
                    environment {
                        DOCKER_FILE_PATH = "/.docker/config.json"
                    }
                    steps {
                        script {
                            sh "${bob} eric-product-info-check"
                            sh "${bob} add-experimental-permissions-for-docker-config-file"
                            sh '''
                                {
                                    while IFS= read -r image; do
                                        docker manifest inspect $image >> manifest_inspect_information.txt

                                        if [ $? -eq 0 ]
                                        then
                                            echo "Manifest command successful"
                                        else
                                            echo "Manifest command has failed"
                                            echo "ERROR: eric-product-info-check failed"
                                            exit 1
                                        fi
                                    done < image_information_list.txt
                                } || {
                                    echo "Manifest command has failed"
                                }
                            '''
                        }
                    }
                }
                stage('Run App validator Schema Tests') {
                    when {
                        expression { params.SCHEMA_TESTS_PATH != "None" }
                    }
                    steps {
                        script {
                            withCredentials([file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE')]) {
                                sh "${bob} validate-chart-schema:validate validate-chart-schema:test_schema"
                            }
                        }
                    }
                }
                stage('Check shell scripts') {
                    steps {
                        script{
                            echo "Running shellcheck on full cloned repo"
                            sh "${bob} shellcheck:run-shellcheck-on-cloned-repo"
                        }
                    }
                }
                stage('Lint YAML files') {
                    steps {
                        sh "chmod +x -R ${env.WORKSPACE}"
                        sh "${bob} lint:yaml-application-chart"
                    }
                }
                stage('Python Lint') {
                    when {
                        expression { does_commit_contain_file_type(".py") == true }
                    }
                    steps {
                        script {
                            sh "${bob} pylint"
                        }
                    }
                }
                stage('Helm Lint') {
                    steps {
                        sh "${bob} lint:helm"
                    }
                }
                stage('Validate Static Tests Site Values against Built Chart'){
                    steps {
                        sh "${bob} run-helm-chart-validator-testsuite:validate-chart-against-schema-file"
                    }
                }
                stage('Run App validator Static Tests') {
                    steps {
                        script {
                            withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                                sh "${bob} run-helm-chart-validator-testsuite:helm-template run-helm-chart-validator-testsuite:helm-chart-validator"
                            }
                        }
                    }
                    post {
                        always {
                            sh "mv report.html helm-chart-validator-test-report.html"
                        }
                    }
                }
                stage('ADP Design Rules Setup and Execution'){
                    steps {
                        script {
                            DESIGN_RULE_OPTIONS_SERVICE = sh (
                                script:'cat ${WORKSPACE}/${DESIGN_RULES_PATH}/${APP_NAME}/design_rule_options.txt | tr "\n" " "',
                                returnStdout: true
                            ).trim()
                            echo "DEBUG: SERVICE DEFINED SKIP(S): ${DESIGN_RULE_OPTIONS_SERVICE}"

                            DESIGN_RULE_OPTIONS_COMMON = sh (
                                script:'cat ${WORKSPACE}/${DESIGN_RULES_PATH}/common_design_rule_options.txt | tr "\r\n" " " | tr "  " " "',
                                returnStdout: true
                            ).trim()
                            echo "DEBUG: COMMON SKIP(S): ${DESIGN_RULE_OPTIONS_COMMON}"

                            DESIGN_RULE_OPTIONS = DESIGN_RULE_OPTIONS_SERVICE + " " + DESIGN_RULE_OPTIONS_COMMON
                            echo "DEBUG: SKIPS COMBINED: ${DESIGN_RULE_OPTIONS}"

                            if ( params.FULL_CHART_SCAN.toLowerCase() == "true" ) {
                                // Parameters to test only triggered microservice dependency chart
                                def CHART_PACKAGE = findFiles(glob: "${env.APP_NAME}-*.tgz")
                                DR_PARAMETERS = "--helm-chart ${CHART_PACKAGE[0].path} " + "-DhelmDesignRule.feature.dependency=0 "
                            } else {
                                // Check only top level chart if job triggered from REFSPEC
                                def CHART_PACKAGE = findFiles(glob: "${env.APP_NAME}-*.tgz")
                                DR_PARAMETERS = "--helm-chart ${CHART_PACKAGE[0].path} " + "-DhelmDesignRule.feature.dependency=1 "
                            }
                            echo "DR_PARAMETERS: ${DR_PARAMETERS}"
                            // Put DR commands in front of provided in parameters DESIGN_RULE_OPTIONS
                            DESIGN_RULE_OPTIONS = DR_PARAMETERS + DESIGN_RULE_OPTIONS
                            echo "DESIGN_RULE_OPTIONS: ${DESIGN_RULE_OPTIONS}"
                            env.DESIGN_RULE_OPTIONS = DESIGN_RULE_OPTIONS

                            withCredentials([file(credentialsId: env.HELM_REPO_CREDENTIALS_ID, variable: 'HELM_REPO_CREDENTIALS_FILE')]) {
                                sh "install -m 600 ${HELM_REPO_CREDENTIALS_FILE} ${HELM_REPO_CREDENTIALS}"
                                sh "${bob} common-design-rule-checker"
                            }
                        }
                    }
                }
            }
        }
    }
    post {
         success {
            script {
                if (params.GERRIT_REFSPEC != '')
                    sh "${gerritReviewCommand} --message '\"Build Successful: ${BUILD_URL} : SUCCESS\"'"
            }
         }
         failure {
            script {
                if (params.GERRIT_REFSPEC != '')
                    sh "${gerritReviewCommand} --message '\"Build Failed: ${BUILD_URL} : FAILURE\"'"
                    if (getContext(hudson.FilePath)) {
                        sh "printenv | sort"
                        archiveArtifacts artifacts: ".bob/cloned_repo/testsuite/site_values.yaml, manifest_inspect_information.txt, image_information_list.txt,  *.tgz, ci-script-executor-logs/*, yamllint_output.log, yamllint_helm_template_output.yaml", allowEmptyArchive: true, fingerprint: true
                    }
            }
         }
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'image_information_list.json, helm-chart-validator-test-report.html, design-rule-check-report.html, helm-template-manifest.yaml, yamllint_output.log, yamllint_helm_template_output.yaml', allowEmptyArchive: true, fingerprint: true
                }
                sh "mv design-rule-check-report.xml .bob/design-rule-check-report.xml"
                withCredentials([usernamePassword(credentialsId: 'ossapps100-user-creds', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {
                    sh "${bob} common-design-rule-build-notification"
                }
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: '.bob/design-rule-compliance-report.html', allowEmptyArchive: true, fingerprint: true
                }
                modifyBuildDescription()
            }
        }
        cleanup {
            cleanWs()
        }
    }
}

def modifyBuildDescription() {
    // Helm DR build notification
    def helm_dr_compliance_report = ".bob/design-rule-compliance-report.html"
    def helm_dr_compliance_data =  ""
    if (fileExists("${workspace}/${helm_dr_compliance_report}")) {
        helm_dr_compliance_data = readFile(helm_dr_compliance_report).trim()
    }

    if (currentBuild.description != null) {
        currentBuild.description = currentBuild.description + "${helm_dr_compliance_data}"
    } else {
        currentBuild.description = "${helm_dr_compliance_data}"
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

def does_commit_contain_file_type(file_extension) {
    def commit_sha = sh(returnStdout: true, script: "git -C \$PWD/.bob/cloned_repo log --pretty=format:'%H' -n 1").trim()
    def files_changed = sh(returnStdout: true, script: "git -C \$PWD/.bob/cloned_repo show --pretty='format:' --name-only --diff-filter=dr ${commit_sha}").trim()
    for (file in files_changed.split("\n")) {
        if (file.endsWith(file_extension)) {
            return true
        }
    }
    return false
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
