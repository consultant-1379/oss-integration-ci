#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */
def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review \${GERRIT_PATCHSET_REVISION}"
def RETRY_KUBERNETES_CHECKS_ATTEMPT = 1
def RETRY_OPENSHIFT_CHECKS_ATTEMPT = 1
def RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT = 1
def RETRY_CLEANING_GIT_REPO_ATTEMPT = 1
def RETRY_FETCH_HELMFILE_REPO_ATTEMPT = 1
def RETRY_GENERATE_SITE_VALUES_ATTEMPT = 1
def RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT = 1

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
        string( name: 'GERRIT_USER_SECRET',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'FUNCTIONAL_USER_SECRET',
                description: 'Jenkins secret ID for ARM Registry Credentials')
        string(name: 'ARMDOCKER_USER_SECRET',
                description: 'Jenkins secret ID with ARM Docker config details')
        string( name: 'GERRIT_PROJECT',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss.eiae/eiae-helmfile')
        string( name: 'CHART_PATH',
                description: 'Relative path to helm chart in git repo.')
        string( name: 'INT_CHART_NAME',
                description: 'Helmfile name, e.g. eric-eiae-helmfile')
        string( name: 'INT_CHART_VERSION',
                description: 'Helmfile verison')
        string( name: 'INT_CHART_REPO',
                description: 'Helmfile repo, e.g. https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm')
        string( name: 'PATH_TO_SITE_VALUES_FILE',
                description: 'The full path to the ci site values template file for the Helmfile under test')
        string( name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
                description: 'The full path to the ci site values override template file for the additional values needed for the Helmfile under test')
        string( name: 'KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH',
                description: 'The full path to the kubernetes compatibility site values file used during the Kubernetes Testing Phase')
        string( name: 'HELMFILE_NAME',
                description: 'The name of the Helmfile under test e.g. eiae-helmfile/eo-helmfile. Very important as it is used to set the build name and conditionally run certain Helmfile-specific stages')
        string( name: 'KUBEVAL_KINDS_TO_SKIP',
                description: 'Skipped Kubeval checks for specific kinds.')
        string( name: 'SPINNAKER_PIPELINE_ID',
                defaultValue: '123456',
                description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.')
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
        string( name: 'VCS_BRANCH',
                defaultValue: 'master',
                description: 'Branch for the change to be pushed')
        string( name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string( name: 'CI_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Refspec for testing')
    }
    agent {
        label env.SLAVE_LABEL
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        TIMESTAMP = sh(script: "echo `date +%s`", returnStdout: true).trim()
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        CHART_PATH = ".bob/cloned_repo/helmfile/${env.CHART_PATH}"

        HELMFILE_NAME = "${params.HELMFILE_NAME}"
        HELMFILE_PATH_FOR_OPTIONALITY="${env.WORKSPACE}/.bob/cloned_repo/helmfile"
        PATH_FOR_OPTIMIZED_FILE="${env.WORKSPACE}/.bob/cloned_repo/helmfile_optimized"
        FULL_PATH_TO_SITE_VALUES_FILE = "${env.WORKSPACE}/${params.PATH_TO_SITE_VALUES_FILE}"
        FULL_PATH_TO_HELMFILE_TEMPLATE_OVERRIDE_FILE = "${env.WORKSPACE}/${params.PATH_TO_SITE_VALUES_OVERRIDE_FILE}"
        STATE_VALUES_FILE = "${env.WORKSPACE}/site_values.yaml"

        HELMFILE_VALIDATOR_DIRECTORY_PATH = "testsuite/common/helmfile-validator"
        COMMON_SKIP_LIST_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/common_skip_list.json"
        SPECIFIC_SKIP_LIST_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/${env.HELMFILE_NAME}/skip_list.json"
        CHECK_SPECIFIC_CONTENT_FILE_PATH = "${env.WORKSPACE}/${env.HELMFILE_VALIDATOR_DIRECTORY_PATH}/${env.HELMFILE_NAME}/check_specific_content.json"

        FULL_PATH_TO_YAMLLINT_CONFIG_FILE = "/ci/jenkins/config/yamllint_config.yaml"
        TEMPLATE_OUTPUT_FILE_PATH = "${env.WORKSPACE}/yamllint_helmfile_template_output.yaml"
        YAMLLINT_OUTPUT_FILE_PATH = "${env.WORKSPACE}/yamllint_output.log"

        KUBERNETES_TESTS_PATH = "testsuite/kubernetes-tests"
        KUBE_VERSION_FILE_PATH="${env.WORKSPACE}/${env.KUBERNETES_TESTS_PATH}/kubeVersion.yaml"
        SITE_VALUES_FILE_PATH_FOR_KUBERNETES_COMPATIBILITY_CHECKS = "${env.WORKSPACE}/${params.KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH}"
        HELMFILE_OR_HELM_CHART_FILE_PATH="${env.WORKSPACE}/.bob/cloned_repo/helmfile_optimized/helmfile.yaml"
    }
    stages{
        stage('Set Build Name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${HELMFILE_NAME}"
                }
            }
        }
        stage('Gerrit notification - build started') {
            when {
                expression { params.GERRIT_PATCHSET_REVISION != '' }
            }
            steps {
                script {
                    sh "${gerritReviewCommand} --message '\"Build Started: ${BUILD_URL}\"'"
                }
            }
        }
        stage('Cleaning Git Repo') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_CLEANING_GIT_REPO_ATTEMPT > 1) {
                            echo "Rerunning the \"Cleaning Git Repo\" stage. Retry ${RETRY_CLEANING_GIT_REPO_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Cleaning Git Repo\" stage. Try ${RETRY_CLEANING_GIT_REPO_ATTEMPT} of 5"
                        }
                        RETRY_CLEANING_GIT_REPO_ATTEMPT = RETRY_CLEANING_GIT_REPO_ATTEMPT + 1

                        command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                        command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                        sh "${bob} git-clean"
                        RETRY_CLEANING_GIT_REPO_ATTEMPT = 1
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
                    if (env.CI_DOCKER_IMAGE == "local") {
                        sh "${bobInternal} build-local-python-ci-image"
                    }
                }
            }
        }
        stage('Fetch Helmfile Repo') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_FETCH_HELMFILE_REPO_ATTEMPT > 1) {
                            echo "Rerunning the \"Fetch Helmfile Repo\" stage. Retry ${RETRY_FETCH_HELMFILE_REPO_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Fetch Helmfile Repo\" stage. Try ${RETRY_FETCH_HELMFILE_REPO_ATTEMPT} of 5"
                        }
                        RETRY_FETCH_HELMFILE_REPO_ATTEMPT = RETRY_FETCH_HELMFILE_REPO_ATTEMPT + 1

                        if(env.HELMFILE_NAME != "ci-inca-helmfile"){
                            withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                                sh "${bobInternal} gerrit:clone-repo-restricted"
                            }
                        }

                        if (env.GERRIT_REFSPEC != "") {
                            withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]){
                                sh "${bobInternal} gerrit:checkout-patch"
                            }
                        }
                        else {
                            withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]){
                                sh "${bob} fetch-helmfile untar-and-copy-helmfile-to-cloned-repo"
                            }
                        }
                        RETRY_FETCH_HELMFILE_REPO_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Generate State Site Values File') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_GENERATE_SITE_VALUES_ATTEMPT > 1) {
                            echo "Rerunning the \"Generate State Site Values File\" stage. Retry ${RETRY_GENERATE_SITE_VALUES_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Generate State Site Values File\" stage. Try ${RETRY_GENERATE_SITE_VALUES_ATTEMPT} of 5"
                        }
                        RETRY_GENERATE_SITE_VALUES_ATTEMPT = RETRY_GENERATE_SITE_VALUES_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh "${bob} run-helmfile-validator:gather-site-values-file"
                        }

                        RETRY_GENERATE_SITE_VALUES_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Generate Optionality File') {
            steps {
                retry(count: 5){
                    script {
                        if (RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT > 1) {
                            echo "Rerunning the \"Generate Optionality File\" stage. Retry ${RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Generate Optionality File\" stage. Try ${RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT} of 5"
                        }
                        RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT = RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh "${bob} generate-optionality-maximum"
                        }

                        RETRY_GENERATE_OPTIONALITY_FILE_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Run Precode Testing'){
            parallel{
                stage('Check files executable permission') {
                    when {
                        /*Skipping if checking on a built Helmfile version/Snapshot Version due to permission issues that requires root user permissions when untarring*/
                        expression { params.GERRIT_REFSPEC != '' }
                    }
                    steps {
                        script{
                            echo "Beginning Check files executable permission stage"
                            def prFiles = getFiles("${env.WORKSPACE}/.bob/cloned_repo")
                            def nonexecutableFiles = []
                            for (file in prFiles.split('\n')) {
                                if (file.endsWith('.sh') || file.endsWith('.py')) {
                                    def isExecutable = sh(script: "[[ -x \"${env.WORKSPACE}/.bob/cloned_repo/$file\" ]]", returnStatus: true) == 0
                                    if (!isExecutable) {
                                        nonexecutableFiles.add(file)
                                    }
                                }
                            }
                            if (nonexecutableFiles) {
                                echo """
                                        +-------------------------------------------------------------------------+
                                        ERROR: Non Executable files found in your patch.
                                        +-------------------------------------------------------------------------+
                                        ${nonexecutableFiles.join('\n\t\t\t\t')}
                                        +-------------------------------------------------------------------------+
                                        Note: Please ensure the listed files are executable.
                                    """
                                error "Non-executable file found."
                            } else {
                                echo "Check files executable permission stage has been successfully tested"
                            }
                        }
                    }
                }
                stage('Lint YAML files') {
                    steps {
                        sh "chmod +x -R ${env.WORKSPACE}"
                        sh "${bob} lint:yaml-helmfile"
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
                stage('Validate Helm Chart Schema') {
                    when {
                        expression {
                             params.VCS_BRANCH.equals('master') && !(params.CHART_PATH.equals(''))
                        }
                    }
                    steps {
                        script {
                            echo "Running the \"Validate Helm Chart Schema\" stage."
                            if (params.CHART_PATH.contains(',')) {
                                def charts = "${params.CHART_PATH}".split(',')
                                charts.each { chart ->
                                    withEnv(["CHART_PATH=.bob/cloned_repo/helmfile/${chart}"]) {
                                        echo "Validating Helm Chart schema of ${env.CHART_PATH}"
                                        sh "${bob} validate-chart-schema:validate"
                                    }
                                }
                            } else {
                                sh "${bob} validate-chart-schema:validate"
                            }
                        }
                    }
                }
                stage('Validate Helm Site-Values Schema') {
                    when {
                        expression { params.HELMFILE_NAME.equals('eiae-helmfile') }
                    }
                    steps {
                        script {
                            echo "Running the \"Validate Helm Site-Values Schema\" stage."
                            sh "${bob} validate-site-values-template-schema"
                        }
                    }
                }
                stage('Validating eric-product-info images'){
                    environment {
                        CHART_PATH = ".bob/cloned_repo/helmfile"
                        DOCKER_FILE_PATH = ".docker/config.json"
                    }
                    steps {
                        retry(count: 5){
                            script {
                                if (RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT > 1) {
                                    echo "Rerunning the \"Validating eric-product-info images\" stage. Retry ${RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(60)
                                }
                                else {
                                    echo "Running the \"Validating eric-product-info images\" stage. Try ${RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT} of 5"
                                }
                                RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT = RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT + 1

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

                                RETRY_VALIDATE_ERIC_PRODUCT_INFO_ATTEMPT = 1
                            }
                        }
                    }
                }
                stage('Run Helmfile Openshift Static Tests') {
                    when {
                        expression {
                             params.VCS_BRANCH.equals('master')
                        }
                    }
                    steps {
                        retry(count: 5){
                            script {
                                if (RETRY_OPENSHIFT_CHECKS_ATTEMPT > 1) {
                                    def exitCode = sh (script: 'find . -name "*helmfile_static_tests.log"', returnStatus: true)
                                    if (exitCode == 0) {
                                        echo 'helmfile-static-tests failed. Please see log attached'
                                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                                            sh "exit 1"
                                        }
                                        return
                                    }
                                    echo "Rerunning the \"Run Helmfile Openshift Static Tests\" stage. Retry ${RETRY_OPENSHIFT_CHECKS_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(60)
                                }
                                else {
                                    echo "Running the \"Run Helmfile Openshift Static Tests\" stage. Try ${RETRY_OPENSHIFT_CHECKS_ATTEMPT} of 5"
                                }
                                RETRY_OPENSHIFT_CHECKS_ATTEMPT = RETRY_OPENSHIFT_CHECKS_ATTEMPT + 1

                                withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                                    sh "${bob} run-helmfile-validator:helmfile-template"
                                    sh "${bob} run-helmfile-validator:helmfile-validator"
                                }

                                RETRY_OPENSHIFT_CHECKS_ATTEMPT = 1
                            }
                        }
                    }
                    post {
                        always {
                            sh "mv report.html helmfile-validator-test-report.html"
                        }
                    }
                }
                stage('Lint - Helmfile Build output') {
                    steps {
                        withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh "${bob} run-helmfile-validator:helmfile-build"
                            sh "${bob} run-helmfile-validator:helmfile-lint"
                        }
                    }
                }
                stage('Run Kubernetes Range Compatibility Tests') {
                    steps {
                        retry(count: 5){
                            script {
                                if (RETRY_KUBERNETES_CHECKS_ATTEMPT > 1) {
                                    echo "Rerunning the \"Run Kubernetes Range Compatibility Tests\" stage. Retry ${RETRY_KUBERNETES_CHECKS_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(60)
                                }
                                else {
                                    echo "Running the \"Run Kubernetes Range Compatibility Tests\" stage. Try ${RETRY_KUBERNETES_CHECKS_ATTEMPT} of 5"
                                }
                                RETRY_KUBERNETES_CHECKS_ATTEMPT = RETRY_KUBERNETES_CHECKS_ATTEMPT + 1

                                withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                                    def compatibility_tests_command = "${bob} run-kubernetes-compatibility-tests"
                                    def exit_status_of_command = sh(script: compatibility_tests_command, returnStatus: true)
                                    if (exit_status_of_command == 255) {
                                        echo 'Kubernetes compatibility tests failed.'
                                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                                            sh "exit 1"
                                        }
                                    } else if (exit_status_of_command == 0 ) {
                                        echo 'Kubernetes compatibility tests passed.'
                                    } else {
                                        sh(script: 'exit 1')
                                    }

                                    def tests_kubeval_and_deprek8ion= "${bob} run-kubernetes-compatibility-tests-kubeval-and-deprek8ion-tests"
                                    def exit_status = sh(script: tests_kubeval_and_deprek8ion, returnStatus: true)
                                    if (exit_status == 255) {
                                        echo 'Kubernetes tests-kubeval-and-deprek8ion failed.'
                                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                                            sh "exit 1"
                                        }
                                    } else if (exit_status == 0) {
                                        echo 'Kubernetes tests-kubeval-and-deprek8ion passed.'
                                    } else {
                                        sh(script: 'exit 1')
                                    }
                                }

                                RETRY_KUBERNETES_CHECKS_ATTEMPT = 1
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
                archiveArtifacts artifacts: "helmfile-build-manifest.yaml, helmfile-template-manifest.yaml, image_information_list.json, manifest_inspect_information.txt, helmfile-validator-test-report.html, site_values.yaml, yamllint_output.log, yamllint_helmfile_template_output.yaml", allowEmptyArchive: true, fingerprint: true
                if (params.GERRIT_PATCHSET_REVISION != '')
                    sh "${gerritReviewCommand} --message '\"Build Successful: ${BUILD_URL} : SUCCESS\"'"
            }
        }
        failure {
            script {
                archiveArtifacts artifacts: "ci-script-executor-logs/*, helmfile-build-manifest.yaml, helmfile-template-manifest.yaml, site_values.yaml, yamllint_output.log, yamllint_helmfile_template_output.yaml", allowEmptyArchive: true, fingerprint: true
                if (params.GERRIT_PATCHSET_REVISION != '')
                    sh "${gerritReviewCommand} --message '\"Build Failed: ${BUILD_URL} : FAILURE\"'"
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

def getFiles(path) {
    if (params.GERRIT_REFSPEC != '')
    {
        // Return files changed in commit
        return sh(returnStdout: true, script: "cd $path && git diff-tree --diff-filter=ACM --no-commit-id --name-only -r $GERRIT_PATCHSET_REVISION -- $path | xargs -I {} find {} -type f").trim()
    }
    // Return all .sh and .py files in the path
    return sh(returnStdout: true, script: "find $path -type f -name '*.sh' -o -name '*.py'").trim()
}

def does_commit_contain_file_type(file_extension, path) {
    def commit_sha = sh(returnStdout: true, script: "cd $path && git -C ./ log --pretty=format:'%H' -n 1").trim()
    def files_changed = sh(returnStdout: true, script: "cd $path && git -C ./ show --pretty='format:' --name-only --diff-filter=dr ${commit_sha}").trim()
    for (file in files_changed.split("\n")) {
        if (file.endsWith(file_extension)) {
            return true
        }
    }
    return false
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
