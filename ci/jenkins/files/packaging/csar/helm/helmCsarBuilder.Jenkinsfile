#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        booleanParam(name: 'RELEASE', defaultValue: true, description: 'Release the CSAR to Nexus')
        string( name: 'INT_CHART_NAMES',
                description: 'Chart Name of Chart(s) to build from. Multiple charts can be included, using \",\" separation only. NOTE: The first chart name will be used to set the CSAR name.')
        string( name: 'INT_CHART_VERSIONS',
                description: 'Version(s) of the Chart to build from. Multiple versions can be included, using \",\" separation only. NOTE: Versions should be in the same order as the Chart Name.')
        string( name: 'INT_CHART_REPOS',
                description: 'Repo(s) to fetch the chart from. Multiple repos can be included, using \",\" separation only. NOTE: Repos should be in the same order as the Chart Name.')
        string(name: 'HELMFILE_CHART_NAME',
                description: 'Name of the helmfile to be retrieved to run the helmfile template - e.g., eric-eiae-helmfile.')
        string(name: 'HELMFILE_CHART_VERSION',
                description: 'The version of the helmfile to be retrieved to run the helmfile template.')
        string(name: 'HELMFILE_CHART_REPO',
                description: 'The repository to retrieve the helmfile.')
        string(name: 'STATE_VALUES_FILE',
                defaultValue: 'None',
                description: 'The site values file for the helmfile template command.')
        string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
                description: 'The site values override file for the helmfile template command.')
        string( name: 'SSH_REPO_URL',
                defaultValue: 'None',
                description: 'SSH URL to the repo that holds the pre-populated site values file and if required the scripts that should be included in the CSAR.')
        string( name: 'FORCE_CSAR_REBUILD',
                defaultValue: 'false',
                description: 'Used to force a rebuild of the CSAR when set to true, even if there is a version already released into the ARM registry. Use with caution')
        string( name: 'USE_TAG',
                defaultValue: 'true',
                description: 'Used to checkout the tag associates to the chart being built, to ensure the correct site values/scripts are used. If a tag is not found the master of the repo is checkout')
        string( name: 'USE_ERIC_PRODUCT_INFO',
                defaultValue: 'false',
                description: 'Use --eric-product-info tag within the CSAR Builder to collect images from the eric-product-info.yaml instead of gathering images via the helm template command with given site-values file')
        string( name: 'SCRIPTS_DIR',
                defaultValue: 'None',
                description: 'Scripts directory within the SSH Repo URL specified. The content of this directory will be copied to the /scripts directory on the CSAR')
        string( name: 'POPULATED_VALUES_FILE_LOCATION',
                description: 'Full Path to the populated site values file within the SSH Repo URL (e.g. site-values/csar-build/config-handling/site-values.yaml). This file will be used to execute a helm template to get all the appropriate docker images to be included in the CSAR.')
        string( name: 'CSAR_STORAGE_INSTANCE',
                defaultValue: 'arm.seli.gic.ericsson.se',
                description: 'Storage Instance to push the CSARs to. NOTE: Use Default if unsure')
        string( name: 'CSAR_STORAGE_REPO',
                defaultValue: 'proj-eric-oss-drop-generic-local',
                description: 'Storage directory to push the CSARs to. NOTE: Use Default if unsure')
        string(name: 'ARMDOCKER_USER_SECRET',
                description: 'ARM Docker secret')
        string(name: 'FUNCTIONAL_USER_SECRET',
                description: 'Jenkins secret ID for ARM Registry Credentials')
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
        string(name: 'DISTRIBUTION_EMAILS',
                defaultValue: 'PDLTICKETM@pdl.internal.ericsson.com',
                description: 'A list of emails to inform if an existing CSAR is overwritten')
        string(name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CSAR_STORAGE_API_URL = get_csar_storage_url("${params.CI_DOCKER_IMAGE}")
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        BUILD_CSAR_OPTION = get_build_csar_option("${params.USE_ERIC_PRODUCT_INFO}", "${params.POPULATED_VALUES_FILE_LOCATION}")
        BUILD_CSAR_TYPE = '--helm'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
                sh "${bob} csar-management:set-empty-optional-values"
                sh "${bob} csar-management:set-empty-product-info"
            }
        }
        stage('Inject Creds') {
            steps {
                withCredentials( [file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'dockerConfig')]) {
                    sh "mkdir ${WORKSPACE}/.docker"
                    sh "install -m 666 ${dockerConfig} ${WORKSPACE}/.docker/config.json"
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
        stage('Get Base Helm Chart Version(s)') {
            steps {
                script {
                    ( chartDetailsMap, intChartFullNames ) = BuildChartList("all")
                    chartDetailsMap.each { item ->
                        env.ARTIFACT_FULL_NAME = intChartFullNames
                        env.INT_CHART_NAME = item.key
                        item.value.each { value ->
                            if ( value.key == "version" ) {
                                env.INT_CHART_VERSION = value.value
                            }
                            if ( value.key == "repo" ) {
                                env.INT_CHART_REPO = value.value
                            }
                        }
                        echo "INT_CHART_NAME = ${env.INT_CHART_NAME}"
                        echo "INT_CHART_VERSION = ${env.INT_CHART_VERSION}"
                        echo "INT_CHART_REPO = ${env.INT_CHART_REPO}"
                        // ARTIFACT_FULL_NAME variable is used when building the csar at a later stage.
                        echo "ARTIFACT_FULL_NAME = ${env.ARTIFACT_FULL_NAME}"
                        writeFile file: "manifest.txt", text: "${env.ARTIFACT_FULL_NAME}"
                        withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} fetch-chart"
                        }

                    }
                }
            }
        }
        stage('Set CSAR Environment Variables') {
            steps {
                script {
                    ( chartDetailsMap, intChartFullNames ) = BuildChartList("csar-details")
                    chartDetailsMap.each { item ->
                        env.ARTIFACT_NAME = item.key
                        item.value.each { value ->
                            if ( value.key == "version" ) {
                                env.ARTIFACT_VERSION = value.value
                            }
                            if ( value.key == "repo" ) {
                                env.ARTIFACT_REPO = value.value
                            }
                        }
                        echo "ARTIFACT_NAME = ${env.ARTIFACT_NAME}"
                        echo "ARTIFACT_VERSION = ${env.ARTIFACT_VERSION}"
                        echo "ARTIFACT_REPO = ${env.ARTIFACT_REPO}"
                    }
                }
            }
        }
        stage('Clone Repo for optional scripts directory') {
            when {
                expression { params.SSH_REPO_URL != "None" }
            }
            steps {
                script {
                    sh '''
                        bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml clone-repo
                        if [[ "${USE_TAG}" == "true" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml check-out-version-tag
                        fi
                        if [[ "${SCRIPTS_DIR}" != "None" && "${POPULATED_VALUES_FILE_LOCATION}" != "None" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml fetch-contents-for-scripts-directory fetch-values-from-repo csar-management:set-scripts-and-values-file
                        elif [[ "${SCRIPTS_DIR}" == "None" && "${POPULATED_VALUES_FILE_LOCATION}" != "None" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml fetch-values-from-repo csar-management:set-values-file-only
                        elif [[ "${SCRIPTS_DIR}" != "None" && "${POPULATED_VALUES_FILE_LOCATION}" == "None" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml fetch-contents-for-scripts-directory csar-management:set-script-dir-only
                        fi
                    '''
                }
            }
        }
        stage('Check for existing CSAR version in CSAR repo') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} build-application-list-file check-for-existing-csar-in-repo"
                }
            }
        }
        stage('Evaluate existing images') {
            environment {
                CSAR_OUTPUT_FILE = "${env.WORKSPACE}/full-site-values-for-csar-build-info.yaml"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                        sh '''
                            csar_found=$(cat build_csar.properties | grep csar_found | sed 's/=/ /' | awk '{print $2}')

                            if [[ "$csar_found" == "True" && "$FORCE_CSAR_REBUILD" == "true" ]]; then
                                bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:merge-site-values csar-management:print-site-values-content csar-management:download-and-compare-csar-build-info
                            elif [[ "$csar_found" == "False" ]]; then
                                echo "Skipping the evaluation of existing images as the CSAR does not exist"
                                echo "should_csar_be_built=True" > csar-build-indicator-file.properties
                            else
                                echo "Skipping this stage and subsequent stages as the CSAR exists and there is no rebuild"
                                echo "should_csar_be_built=False" > csar-build-indicator-file.properties
                            fi
                        '''
                    }
                }
            }
        }
        stage('Build the CSAR') {
            environment {
                CSAR_OUTPUT_FILE = "${env.WORKSPACE}/site-values-populated.yaml"
            }
            steps {
                retry(count: 5) {
                    withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                        script {
                            if (RETRY_ATTEMPT > 1) {
                                echo "Rerunning the \"Build the CSAR'\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                sleep(180)
                            }
                            else {
                                echo "Running the \"Build the CSAR'\" stage. Try ${RETRY_ATTEMPT} of 5"
                            }
                            RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                            sh '''
                                should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')
                                chart=$( echo $INT_CHART_NAMES | sed 's/,/ /g' | awk '{print $1}' )

                                if [[ "$should_csar_be_built" == "True" ]]; then
                                    if [[ "${BUILD_CSAR_OPTION}" == "build-csar-with-eric-product-info-without-site-values" ]]; then
                                        bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:set-eric-product-info-disable-helm-template
                                    elif [[ "${BUILD_CSAR_OPTION}" == "build-csar-with-eric-product-info" ]]; then
                                        bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:set-eric-product-info-only
                                    fi
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:set-default-values
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:build-csar
                                else
                                    echo "Skipping the CSAR build stage"
                                fi
                            '''
                            RETRY_ATTEMPT = 1
                        }
                    }
                }
            }
        }
        stage('Compare images within CSAR to those within the helmfile') {
            when {
                expression { params.USE_ERIC_PRODUCT_INFO == "false" }
            }
            environment {
                CSAR_OUTPUT_FILE = "${env.WORKSPACE}/full-site-values.yaml"
            }
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    script {
                        sh '''
                            should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')

                            if [[ "$should_csar_be_built" == "True" ]]; then
                                bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:merge-site-values csar-management:print-site-values-content csar-management:compare-images-between-helmfile-and-csar
                            else
                                echo "Skipping the image comparison stage"
                            fi
                        '''
                    }
                }
            }
        }
        stage('Combine the manifest and images information') {
            steps {
                script {
                    sh '''
                        should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')

                        if [[ "$should_csar_be_built" == "True" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:combine-csar-manifest-and-images-info
                        else
                            echo "Skipping the manifest and images information combination stage"
                        fi
                    '''
                }
            }
        }
        stage('Upload CSAR and obtain local CSAR SHA') {
            parallel {
                stage('Upload CSAR to Storage Location') {
                    steps {
                        script {
                            withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                                sh '''
                                    should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')

                                    if [[ "$should_csar_be_built" == "True" ]]; then
                                        bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:upload-csar csar-management:upload-csar-build-info
                                    else
                                        echo "Skipping the image upload stage"
                                    fi
                                '''
                            }
                        }
                    }
                }
                stage('Getting the SHA of the local CSAR') {
                    steps {
                        script {
                            sh '''
                                should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')

                                if [[ "$should_csar_be_built" == "True" ]]; then
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:get-local-csar-sha
                                else
                                    echo "Skipping getting the local CSAR SHA"
                                fi
                            '''
                        }
                    }
                }
            }
        }
        stage('Compare the local and online CSAR SHA') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                        sh '''
                            should_csar_be_built=$(cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}')

                            if [[ "$should_csar_be_built" == "True" ]]; then
                                bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:get-uploaded-csar-sha csar-management:compare-sha-values
                            else
                                echo "Skipping the SHA comparison"
                            fi
                        '''
                    }
                }
            }
        }
        stage('Send CSAR overwrite email'){
            steps {
                script {
                    if (params.FORCE_CSAR_REBUILD == "true") {
                        def should_csar_be_built = sh(script: '''
                            cat csar-build-indicator-file.properties | grep should_csar_be_built | sed 's/=/ /' | awk '{print $2}'
                        ''', returnStdout: true).trim()
                        def csar_found = sh(script: '''
                            cat build_csar.properties | grep csar_found | sed 's/=/ /' | awk '{print $2}'
                        ''', returnStdout: true).trim()

                        if (should_csar_be_built == "True" && csar_found == "True") {
                            send_email("A CSAR has been overwritten.", "PDLTICKETM@pdl.internal.ericsson.com, PDLAPPSTAG@pdl.internal.ericsson.com, ${params.DISTRIBUTION_EMAILS}")
                        }
                    }
                }
            }
        }
    }
    post {
        success {
            script {
                sh "rm -f ${env.WORKSPACE}/${env.INT_CHART_NAME}-${env.INT_CHART_VERSION}.csar"
                currentBuild.description = "See published CSAR below:\nhttps://${params.CSAR_STORAGE_INSTANCE}/artifactory/${params.CSAR_STORAGE_REPO}/csars/${env.INT_CHART_NAME}/${env.INT_CHART_VERSION}"
                sh "echo 'INT_CHART_NAME=${params.INT_CHART_NAMES}' > artifact.properties"
                sh "echo 'INT_CHART_REPO=${params.INT_CHART_REPOS}' >> artifact.properties"
                sh "echo 'INT_CHART_VERSION=${params.INT_CHART_VERSIONS}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_INSTANCE=${params.CSAR_STORAGE_INSTANCE}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_REPO=${params.CSAR_STORAGE_REPO}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_LOCATION=csars/${env.INT_CHART_NAME}/${env.INT_CHART_VERSION}' >> artifact.properties"
                sh "echo 'CSAR_NAME=${env.INT_CHART_NAME}-${env.INT_CHART_VERSION}.csar' >> artifact.properties"
                archiveArtifacts 'artifact.properties'
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
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    def csar_build_status = sh(script: '''
                        cat csar-build-status-file.properties | grep csar_build_status | sed 's/=/ /' | awk '{print $2}'
                    ''', returnStdout: true).trim()
                    if (csar_build_status == "Failed") {
                        send_email("A CSAR build has failed from missing images.", "PDLTICKETM@pdl.internal.ericsson.com")
                    }
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
}

def BuildChartList(String chartdetails) {
    def chartNameList = params.INT_CHART_NAMES.split(',')
    def chartVersionList = params.INT_CHART_VERSIONS.split(',')
    def chartRepoList = params.INT_CHART_REPOS.split(',')
    def chartDetailsMap = [:]
    def intChartFullNames = ""
    chartNameList.any { element ->
        def index = chartNameList.findIndexOf { it in element }
        def response = [:]
        response.put("version", chartVersionList[index])
        response.put("repo", chartRepoList[index])
        chartDetailsMap.put(element, response)
        def tmpChartName = "${element}-${chartVersionList[index]}.tgz"
        if ( intChartFullNames == "" ) {
            intChartFullNames = intChartFullNames.concat("${tmpChartName}")
        }
        else {
            intChartFullNames = intChartFullNames.concat(" ${tmpChartName}")
        }
        if ( chartdetails == "csar-details" ) {
            return [ chartDetailsMap, intChartFullNames ]
        }
    }
    return [ chartDetailsMap, intChartFullNames ]
}

def get_csar_storage_url(ci_docker_image) {
    if (!(ci_docker_image.contains("proj-eric-oss-dev"))) {
        return "https://arm.seli.gic.ericsson.se/artifactory/api/storage/proj-eric-oss-drop-generic-local/csars/";
    }
    return "https://arm.seli.gic.ericsson.se/artifactory/api/storage/proj-eric-oss-drop-generic-local/eric-ci-helmfile/csars/";
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

def send_email(email_reason, distribution_emails) {
    def cause = currentBuild.getBuildCauses('hudson.model.Cause$UserIdCause')
    sh """
    echo '''
        This is an automated email to inform you that:
        $email_reason
        As part of the OSS-CSAR-Builder job:
        https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/TicketMaster/job/OSS-CSAR-Builder/<br><br>
        Jenkins build link: $BUILD_URL<br>
        Jenkins user: ${cause.userName}<br>
        CSAR Name: $INT_CHART_NAMES<br>
        CSAR Version: $INT_CHART_VERSIONS<br><br>
        Thank you''' > email.txt
    """
    emailext subject: 'CSAR build notification',
        from: "NoReply@ericsson.com",
        to: "$distribution_emails",
        mimeType: 'text/html',
        body: '${FILE,path="email.txt"}'
}

def get_build_csar_option(String build_csar_option, String csar_build_site_values){
    if (build_csar_option == "true"){
        if (csar_build_site_values == "None"){
            return 'build-csar-with-eric-product-info-without-site-values'
        }
        return 'build-csar-with-eric-product-info'
    }
    return 'build-csar'
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