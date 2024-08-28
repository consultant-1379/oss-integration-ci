#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def skipRemainingStages = false

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
        string( name: 'FORCE_CSAR_REBUILD',
                defaultValue: 'false',
                description: 'Used to force a rebuild of the CSAR when set to true, even if there is a version already released into the ARM registry. Use with caution')
        string( name: 'USE_TAG',
                defaultValue: 'true',
                description: 'Used to checkout the tag associates to the chart being built, to ensure the correct site values/scripts are used. If a tag is not found the master of the repo is checkout')
        string( name: 'SSH_REPO_URL',
                defaultValue: 'None',
                description: 'SSH URL to the repo that holds the scripts that should be included in the CSAR.')
        string( name: 'SCRIPTS_DIR',
                defaultValue: 'None',
                description: 'Scripts directory within the SSH Repo URL specified. The content of this directory will be copied to the /scripts directory on the CSAR')
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
        BUILD_CSAR_OPTION = 'build-csar-with-eric-product-info'
        BUILD_CSAR_TYPE = '--helmfile'
        USE_ERIC_PRODUCT_INFO = true
        ARTIFACT_NAME = "${params.HELMFILE_CHART_NAME}"
        ARTIFACT_VERSION = "${env.HELMFILE_CHART_VERSION}"
        ARTIFACT_REPO = "${env.HELMFILE_CHART_REPO}"
        ARTIFACT_FULL_NAME = "${params.HELMFILE_CHART_NAME}-${env.HELMFILE_CHART_VERSION}.tgz"
        PROPERTIES_FILE = 'tar_file_base_dir_artifact.properties'
    }
    stages {
        stage('Prepare Workspace') {
            steps {
                withCredentials( [file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'dockerConfig')]) {
                    command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                    command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                    sh "${bob} git-clean"
                    sh "mkdir ${WORKSPACE}/.docker"
                    sh "install -m 666 ${dockerConfig} ${WORKSPACE}/.docker/config.json"
                    sh "${bob} csar-management:set-empty-optional-values"
                }
            }
        }
        stage('Get Helmfile') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Get Helmfile\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Get Helmfile\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} helmfile:fetch-helmfile helmfile:extract-helmfile"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Helmfile CSAR Build Check') {
            steps {
                script{
                    withEnv(readFile(PROPERTIES_FILE).split('\n') as List) {
                        if (! fileExists(TAR_BASE_DIR + '/csar')) {
                            currentBuild.result = 'UNSTABLE'
                            skipRemainingStages = true
                        }
                    }
                }
            }
        }
        stage('Clone Repo for optional scripts directory') {
            when {
                allOf {
                    expression {
                        params.SSH_REPO_URL != "None"
                    }
                    expression {
                        !skipRemainingStages
                    }
                }
            }
            steps {
                script {
                    sh '''
                        bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml clone-repo
                        if [[ "${USE_TAG}" == "true" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml check-out-version-tag
                        fi
                        if [[ "${SCRIPTS_DIR}" != "None" ]]; then
                            bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml fetch-contents-for-scripts-directory csar-management:set-script-dir-only
                        fi
                    '''
                }
            }
        }
        stage('Check for existing CSAR version in the CSAR repo') {
            when {
                expression { !skipRemainingStages }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} build-application-list-file check-for-existing-csar-in-repo"
                }
            }
        }
        stage('Evaluate existing images') {
            when {
                expression { !skipRemainingStages }
            }
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
            when {
                expression { !skipRemainingStages }
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

                                if [[ "$should_csar_be_built" == "True" ]]; then
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:set-default-values
                                    bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml csar-management:set-eric-product-info-only
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
        stage('Combine the manifest and images information') {
            when {
                expression { !skipRemainingStages }
            }
            steps {
                script {
                    writeFile file: "manifest.txt", text: "${env.ARTIFACT_FULL_NAME}"
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
        stage('Upload CSAR to Storage Location') {
            when {
                expression { !skipRemainingStages }
            }
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
        stage('Send CSAR overwrite email'){
            when {
                expression { !skipRemainingStages }
            }
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
                sh "rm -f ${env.WORKSPACE}/${env.HELMFILE_CHART_NAME}-${env.HELMFILE_CHART_VERSION}.csar"
                currentBuild.description = "See published CSAR below:\nhttps://${params.CSAR_STORAGE_INSTANCE}/artifactory/${params.CSAR_STORAGE_REPO}/csars/${env.HELMFILE_CHART_NAME}/${env.HELMFILE_CHART_VERSION}"
                sh "echo 'HELMFILE_CHART_NAME=${params.HELMFILE_CHART_NAME}' > artifact.properties"
                sh "echo 'HELMFILE_CHART_VERSION=${params.HELMFILE_CHART_VERSION}' >> artifact.properties"
                sh "echo 'HELMFILE_CHART_REPO=${params.HELMFILE_CHART_REPO}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_INSTANCE=${params.CSAR_STORAGE_INSTANCE}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_REPO=${params.CSAR_STORAGE_REPO}' >> artifact.properties"
                sh "echo 'CSAR_STORAGE_LOCATION=csars/${env.ARTIFACT_NAME}/${env.ARTIFACT_VERSION}' >> artifact.properties"
                sh "echo 'CSAR_NAME=${env.ARTIFACT_NAME}-${env.ARTIFACT_VERSION}.csar' >> artifact.properties"
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
        $email_reason<br><br>
        Jenkins build link: $BUILD_URL<br>
        Jenkins user: ${cause.userName}<br>
        CSAR Name: $HELMFILE_CHART_NAME<br>
        CSAR Version: $HELMFILE_CHART_VERSION<br><br>
        Thank you''' > email.txt
    """
    emailext subject: 'CSAR build notification',
        from: "NoReply@ericsson.com",
        to: "$distribution_emails",
        mimeType: 'text/html',
        body: '${FILE,path="email.txt"}'
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