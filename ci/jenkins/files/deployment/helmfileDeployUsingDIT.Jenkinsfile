#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 *   + c12a011-config-file (admin.config to access c12a011 cluster)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(
            name: 'FLOW_AREA' ,
            defaultValue: 'default' ,
            description: 'Refers to product deployment area. Eg:- eiapaas, release, productstaging, etc. -- aaS Use ONLY'
        )
        string(
            name: 'INT_CHART_VERSION',
            description: 'The version of base platform to install'
        )
        string(
            name: 'INT_CHART_NAME',
            defaultValue: 'eric-eiae-helmfile',
            description: 'Integration Chart Name'
        )
        string(
            name: 'INT_CHART_REPO',
            defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm',
            description: 'Integration Chart Repo'
        )
        string(
            name: 'DEPLOYMENT_TYPE',
            defaultValue: 'install',
            description: 'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string(
           name: 'DEPLOYMENT_NAME',
           description: 'This is the name of the document within the DIT tool that is storing the deployment information'
        )
        string(
            name: 'TAGS',
            description: 'List of tags for applications that have to be deployed, e.g: so adc pf'
        )
        string(
            name: 'SITE_VALUES_FILE_NAME',
            defaultValue: 'site-values-latest.yaml',
            description: 'Name of the site values template to use that is stored in object store, including the file extension'
        )
        string(
            name: 'SITE_VALUE_FILE_BUCKET_NAME',
            defaultValue: 'eic_site_values_template',
            description: 'Name of the bucket that is storing the site values that is stored in object store.'
        )
        string(
            name: 'SITE_VALUES_OVERRIDE_FILE_NAME',
            defaultValue: 'None',
            description: 'Name of the overwrite site values to use that is stored in object store, including the file extension. Content will override the content for the site values set in the SITE_VALUES_FILE_NAME paramater. Set to None if not needed.'
        )
        string(
            name: 'SITE_VALUE_OVERRIDE_BUCKET_NAME',
            defaultValue: 'eic_site_values_override',
            description: 'Name of the bucket that is storing the overwrite site values that is stored in object store. Set to None if not needed.'
        )
        string(
            name: 'IDUN_USER_SECRET',
            defaultValue: 'idun_credentials',
            description: 'Jenkins secret ID for default IDUN user password -- aaS Use ONLY'
        )
        string(
            name: 'PATH_TO_AWS_FILES',
            defaultValue: 'NONE',
            description: 'Path within the Repo to the location of the Idun aaS AWS credentials and config directory -- aaS Use ONLY'
        )
        string(
            name: 'AWS_ECR_TOKEN',
            defaultValue: 'NONE',
            description: 'AWS ECR token for aws public environments for Idun aaS -- aaS Use ONLY'
        )
        string(
            name: 'DOWNLOAD_CSARS',
            defaultValue: 'false',
            description: 'When set to true the script will try to download the officially Released CSARs relation to the version of the applications within the helmfile being deployed. Ensure the DOCKER_REGISTRY and DOCKER_REGISTRY_CREDENTIALS are set also'
        )
        string(
            name: 'DOCKER_REGISTRY',
            defaultValue: 'armdocker.rnd.ericsson.se',
            description: 'Set this to the docker registry to execute the deployment from. Used when deploying from Officially Released CSARs'
        )
        string(
            name: 'DOCKER_REGISTRY_CREDENTIALS',
            defaultValue: 'None',
            description: 'Jenkins secret ID for the Docker Registry. Not needed if deploying from armdocker.rnd.ericsson.se'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
        )
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for ARM Registry Credentials'
        )
        string(
            name: 'FUNCTIONAL_USER_TOKEN',
            defaultValue: 'NONE',
            description: 'Jenkins identity token for ARM Registry access'
        )
        string(
            name: 'DDP_AUTO_UPLOAD',
            defaultValue: 'false',
            description: 'Set it to true when enabling the DDP auto upload and also need to add the DDP instance details into the environment Kube Config file and SITE_VALUES_OVERRIDE_FILE'
        )
        string(
            name: 'USE_DM_PREPARE',
            defaultValue: 'true',
            description: 'Set to true to use the Deployment Manager function \"prepare\" to generate the site values file'
        )
        string(
            name: 'USE_SKIP_IMAGE_PUSH',
            defaultValue: 'false',
            description: 'Set to true to use the Deployment Manager parameter "--skip-image-check-push" in case an image push is done in advance. If false will deploy without the "--skip-image-check-push" parameter'
        )
        string(
            name: 'USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES',
            defaultValue: 'false',
            description: 'Set to true to use the Deployment Manager parameter "--skip-upgrade-for-unchanged-releases" to skip helm upgrades for helm releases whose versions and values have not changed. If false will deploy without the "--skip-upgrade-for-unchanged-releases" parameter'
        )
        string(
            name: 'USE_CERTM',
            defaultValue: 'false',
            description: 'Set to true to use the "--use-certm" tag during the deployment'
        )
        string(
            name: 'COLLECT_LOGS',
            defaultValue: 'true',
            description: 'If set to "true" (by default) - logs will be collected. If false - will not collect logs.'
        )
        string(
            name: 'COLLECT_LOGS_WITH_DM',
            defaultValue: 'false',
            description: 'If set to "false" (by default) - logs will be collected by ADP logs collection script. If true - with deployment-manager tool.'
        )
        string(
            name: 'HELM_TIMEOUT',
            defaultValue: '1800',
            description: 'Time in seconds for the Deployment Manager to wait for the deployment to execute, default 1800'
        )
        string(
            name: 'DOCKER_TIMEOUT',
            defaultValue: '60',
            description: 'Time in seconds for the Deployment Manager to wait for the pulling of docker images to be used for deployment'
        )
        string(
            name: 'VERBOSITY',
            defaultValue: '3',
            description: 'Verbosity Level for Deployment Manager. Verbosity can be from 0 to 4. Default is 3. Set to 4 if debug needed'
        )
        string(
            name: 'TIMEOUT',
            defaultValue: '3600',
            description: 'Time to wait in seconds before the job should timeout')
        string(
            name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out')
        string(
            name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out')
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on'
        )
        string(
            name: 'DEPLOYMENT_MANAGER_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:default',
            description: 'The full image url and tag for the deployment manager to use for the deployment. If the tag is set to default the deployment manager details will be fetched from the dm_version.yaml file from within the helmfile tar file under test'
        )
        string(
            name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows'
        )
        string(
            name: 'CI_GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )

    }
    environment {
        USE_TAGS = 'true'
        STATE_VALUES_FILE = "site_values_${params.INT_CHART_VERSION}.yaml"
        CSAR_STORAGE_URL = get_csar_storage_url("${params.CI_DOCKER_IMAGE}")
        CSAR_STORAGE_API_URL = get_csar_storage_api_url("${params.CI_DOCKER_IMAGE}")
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        PATH_TO_HELMFILE = "${params.INT_CHART_NAME}/helmfile.yaml"
        BUILD_CSAR_TAG ="${params.INT_CHART_NAME}/csar"
        CSAR_STORAGE_INSTANCE = 'arm.seli.gic.ericsson.se'
        CSAR_STORAGE_REPO = 'proj-eric-oss-drop-generic-local'
        FETCH_CHARTS = 'true'
        HELMFILE_CHART_NAME = "${params.INT_CHART_NAME}"
        HELMFILE_CHART_VERSION = "${params.INT_CHART_VERSION}"
        HELMFILE_CHART_REPO = "${params.INT_CHART_REPO}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker_configs"
        SITE_VALUES_FILE_NAME_STRIPPED = strip_file_extension("${params.SITE_VALUES_FILE_NAME}")
        ENV_CONFIG_FILE = "${params.DEPLOYMENT_NAME}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${params.DEPLOYMENT_NAME}"
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
        stage('Download Environment details') {
            steps {
                retry(count: 5) {
                    script {
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Download Environment details\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(20)
                        }
                        else {
                            echo "Running the \"Download Environment details\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} dit:set-document-name dit:download-document-from-dit"
                            sh "mv artifact.properties ${params.DEPLOYMENT_NAME}"
                        }
                        env.NAMESPACE = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^NAMESPACE= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        env.CRD_NAMESPACE = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^CRD_NAMESPACE= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        env.ENV_CERTIFICATES_BUCKET_NAME = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^ENV_CERTIFICATES_BUCKET_NAME= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        env.ENV_FILE_BUCKET_NAME = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^ENV_FILES_BUCKET_NAME= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        env.KUBE_CONFIG = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^KUBE_CONFIG= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        env.CLUSTER_NAME = "${env.KUBE_CONFIG.split("-|_")[0]}"
                        env.PLATFORM = sh (
                            script: "cat ${params.DEPLOYMENT_NAME} | grep ^PLATFORM= | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                        RETRY_ATTEMPT = 1
                    }
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

                        if(params.FUNCTIONAL_USER_TOKEN.trim().toUpperCase() == "NONE" || params.FUNCTIONAL_USER_TOKEN.isEmpty()){
                            withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                                sh "${bob} helmfile:fetch-helmfile"
                            }
                        }else{
                            withCredentials([string(credentialsId: params.FUNCTIONAL_USER_TOKEN, variable: 'FUNCTIONAL_USER_TOKEN')]) {
                                sh "${bob} helmfile:fetch-helmfile-using-token"
                            }
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Set Deployment Manager Version') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Set Deployment Manager Version\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Set Deployment Manager Version\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        sh "${bob} helmfile:extract-helmfile helmfile:get-dm-full-url-version"

                        RETRY_ATTEMPT = 1

                        env.DEPLOYMENT_MANAGER_DOCKER_IMAGE = sh (
                            script: "cat IMAGE_DETAILS.txt | grep ^IMAGE | sed 's/.*=//'",
                            returnStdout: true
                        ).trim()
                    }
                }
            }
        }
        stage('Prepare Working Directory') {
            steps {
                sh "${bob} untar-and-copy-helmfile-to-workdir"
            }
        }
        stage ('Fetch CI Site Values') {
            environment {
                BUCKET_NAME = "${params.SITE_VALUE_FILE_BUCKET_NAME}"
                DATAFILE_NAME = strip_file_extension("${params.SITE_VALUES_FILE_NAME}")
                DATAFILE_TYPE = get_file_extension("${params.SITE_VALUES_FILE_NAME}")
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-datafile-name ost_bucket:set-output-dir ost_bucket:download-files-by-name-in-ost-bucket"
                    sh "mv ${params.SITE_VALUES_FILE_NAME} site_values_${params.INT_CHART_VERSION}.yaml"
                }
            }
        }
        stage('Update CRD Helmfile') {
            when {
                environment ignoreCase: true, name: 'DEPLOY_ALL_CRDS', value: 'true'
            }
            steps {
                sh "${bob} update-crds-helmfile"
                sh "${bob} tar-helmfile-from-workdir"
            }
        }
        stage('Prepare Working Directory Idun aaS') {
            when {
                environment ignoreCase: true, name: 'PLATFORM', value: 'aws'
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Update AWS ECR token in Site values Idun aaS') {
            when {
                not {
                    environment ignoreCase: true, name: 'AWS_ECR_TOKEN', value: 'NONE'
                }
            }
            steps {
                sh "${bob} update-site-values:substitute-aws-ecr-token"
            }
        }
        stage('Update Global Registry within Site Values') {
            when {
                anyOf {
                    environment ignoreCase: true, name: 'DOCKER_REGISTRY', value: 'armdocker.rnd.ericsson.se'
                    allOf {
                        not {
                            environment ignoreCase: true, name: 'DOCKER_REGISTRY', value: 'armdocker.rnd.ericsson.se'
                        }
                        environment ignoreCase: true, name: 'FLOW_AREA', value: 'eiapaas'
                    }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} update-site-values-registry:substitute-global-registry-details"
                }
            }
        }
        stage('Update local Registry within Site Values') {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'DOCKER_REGISTRY', value: 'armdocker.rnd.ericsson.se'
                    }
                    not {
                        environment ignoreCase: true, name: 'FLOW_AREA', value: 'eiapaas'
                    }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.DOCKER_REGISTRY_CREDENTIALS, usernameVariable: 'DOCKER_REGISTRY_USERNAME', passwordVariable: 'DOCKER_REGISTRY_PASSWORD')]) {
                    sh "${bob} update-site-values-registry:substitute-local-registry-details"
                }
            }
        }
        stage('Update Site Values') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Update Site Values'\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Update Site Values'\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} update-site-values:substitute-values-from-env-file"
                            sh "${bob} update-site-values:substitute-application-deployment-option"
                            sh "${bob} update-repositories-file"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Build CSARs') {
            when {
                environment ignoreCase: true, name: 'DOWNLOAD_CSARS', value: 'false'
            }
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Build CSARs\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(180)
                        }
                        else {
                            echo "Running the \"Build CSARs\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} get-release-details-from-helmfile"
                            sh "${bob} helmfile-charts-mini-csar-build"
                            sh "${bob} cleanup-charts-mini-csar-build"
                        }
                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
        stage('Download CSARs') {
            when {
                environment ignoreCase: true, name: 'DOWNLOAD_CSARS', value: 'true'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} helmfile-details:get-version-details"
                    sh '''
                        # Check if there is a csar file, if there is add the Helmfile details to
                        # the artifact.properties file which was generated in get-version-details
                        if [ -f ${BUILD_CSAR_TAG} ]; then
                            echo "${INT_CHART_NAME}=${INT_CHART_VERSION}" >> artifact.properties
                        fi
                    '''
                    sh "${bob} check-for-existing-csar-in-repo"
                    sh "${bob} download-csar-to-workspace"
                }
            }
        }
        stage('Pre Deployment Manager Configuration') {
            stages {
                stage('Deployment Manager Init') {
                    steps {
                        sh "${bob} deployment-manager-init:deployment-manager-init"
                    }
                }
                stage ('Fetch Kube Config') {
                    environment {
                        BUCKET_NAME = "${ENV_FILE_BUCKET_NAME}"
                        BUCKET_OUTPUT_DIR = "kube_config"
                    }
                    steps {
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-output-dir ost_bucket:download-all-files-in-ost-bucket"
                            sh "mv ./${env.BUCKET_OUTPUT_DIR}/${env.KUBE_CONFIG} ./${env.BUCKET_OUTPUT_DIR}/config"
                            sh "chmod 600 ./${env.BUCKET_OUTPUT_DIR}/config"
                        }
                    }
                }
                stage ('Fetch Environment Certs') {
                    environment {
                        BUCKET_NAME = "${ENV_CERTIFICATES_BUCKET_NAME}"
                        BUCKET_OUTPUT_DIR = "certificates"
                    }
                    steps {
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-output-dir ost_bucket:download-all-files-in-ost-bucket"
                        }
                    }
                }
                stage('Prepare Site Values using DM') {
                    when {
                        environment ignoreCase: true, name: 'USE_DM_PREPARE', value: 'true'
                    }
                    steps {
                        retry(count: 5){
                            script{
                                if (RETRY_ATTEMPT > 1) {
                                    if (fileExists('ci-script-executor-logs/ERROR_merge_yaml_files.properties')) {
                                        error("Stage \"Prepare Site Values using DM\" failed.")
                                        return
                                    }
                                    echo "Rerunning the \"Prepare Site Values using DM'\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                    sleep(180)
                                }
                                else {
                                    echo "Running the \"Prepare Site Values using DM'\" stage. Try ${RETRY_ATTEMPT} of 5"
                                }
                                RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                                sh "${bob} prepare-site-values:rename-ci-site-values"

                                if (env.PLATFORM.toLowerCase() == "aws"){
                                    sh "${bob} prepare-site-values:deployment-manager-prepare-idunaas"
                                }
                                else {
                                    sh "${bob} prepare-site-values:deployment-manager-prepare"
                                }
                                sh "${bob} prepare-site-values:populate-prepare-dm-site-values"
                                RETRY_ATTEMPT = 1
                            }
                        }
                    }
                }
            }
            post {
                failure {
                    archiveArtifacts allowEmptyArchive: true, artifacts: "logs/*", fingerprint: true
                }
            }
        }
        stage('Override Site Values') {
            when {
                not {
                    environment ignoreCase: true, name: 'SITE_VALUES_OVERRIDE_FILE_NAME', value: 'None'
                }
            }
            environment {
                BUCKET_NAME = "${params.SITE_VALUE_OVERRIDE_BUCKET_NAME}"
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    update_site_values_with_multiple_files()
                }
            }
        }
        stage('Update Site Values after Override') {
            steps {
                sh "${bob} update-site-values:substitute-values-from-env-file"
                sh "${bob} update-site-values:substitute-application-deployment-option"
                sh "${bob} update-site-values:substitute-application-service-option"
            }
        }
        stage('Update Site Values Idun aaS') {
            when {
                environment ignoreCase: true, name: 'FLOW_AREA', value: 'eiapaas'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-idun-credential"
                }
            }
        }
        stage('Update Site Values with DDP details') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-ddp-details"
                }
            }
        }
        stage('Openshift restricted SCC additions') {
            when {
               environment ignoreCase: true, name: 'PLATFORM', value: 'openshift'
            }
            steps {
                    sh "${bob} openshift-extract-fsgroup"
                    sh "${bob} openshift-write-fsgroup"
                    sh "${bob} openshift-create-scc"
            }
        }
        stage('Create Common Resources') {
            steps {
                sh "${bob} create-common-resources"
            }
        }
        stage ('Helmfile Deployment') {
            stages {
                stage ('Pre-Deployment Helmfile') {
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:remove-local-repositories-yaml"
                        sh "${bob} deploy-helmfile-using-deployment-manager:print-dm-version"
                        sh "${bob} deploy-helmfile-using-deployment-manager:archive-dm-version"
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-skip-image-push-parameter"
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-skip-upgrade-for-unchanged-releases-parameter"
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-use-certm-parameter"
                    }
                }
                stage('Deploy Helmfile') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'PLATFORM', value: 'aws'
                        }
                    }
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile"
                    }
                    post {
                        success {
                            sh "${bob} parse-log-file:parse-deployment-log"

                            retry(count: 5){
                                script{
                                    if (RETRY_ATTEMPT > 1) {
                                        echo "Collecting deployment time data. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                        sleep(30)
                                    }
                                    else {
                                        echo "Collecting deployment time data. Try ${RETRY_ATTEMPT} of 5"
                                    }
                                    RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                                    sh "${bob} get-charts-deployment-time:deployment-time-measurement"

                                    RETRY_ATTEMPT = 1
                                }
                            }

                            archiveArtifacts artifacts: "deploy-timing.yaml", allowEmptyArchive: true, fingerprint: true

                        }
                        failure {
                            script {
                                if (params.COLLECT_LOGS.toLowerCase() == "true"){
                                    if (params.COLLECT_LOGS_WITH_DM.toLowerCase() == "true") {
                                        sh "${bob} gather-logs:gather-deployment-manager-logs || true"
                                    }
                                    else {
                                        sh "${bob} gather-logs:gather-adp-k8s-logs-local || true"
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Deploy Helmfile AWS') {
                    when {
                        environment ignoreCase: true, name: 'PLATFORM', value: 'aws'
                    }
                    steps {
                        script {
                            sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile-idunaas"
                        }
                    }
                    post {
                        success {
                            sh "${bob} parse-log-file:parse-deployment-log"
                        }
                        failure {
                            script {
                                if (params.COLLECT_LOGS.toLowerCase() == "true"){
                                    if (params.COLLECT_LOGS_WITH_DM.toLowerCase() == "true") {
                                        sh "${bob} gather-logs:gather-deployment-manager-logs-idunaas || true"
                                    }
                                    else {
                                        sh "${bob} gather-logs:gather-adp-k8s-logs-local || true"
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
                        sh "${bob} override-functional-password:override-functional-password"
                    }
                }
                success {
                    script {
                        if (params.FLOW_AREA.toLowerCase() == "eiapaas"){
                            sh "${bob} annotate-namespace-installed-helmfile"
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
                    archiveArtifacts allowEmptyArchive: true, artifacts: "artifact.properties, logs_*.tgz, logs/*, ${env.STATE_VALUES_FILE}", fingerprint: true
                }
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
        cleanup {
            cleanWs()
        }
    }
}

def get_csar_storage_url(ci_docker_image) {
    if (!(ci_docker_image.contains("proj-eric-oss-dev"))) {
        return "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/";
    }
    return "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/eric-ci-helmfile/csars/";
}

def get_csar_storage_api_url(ci_docker_image) {
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

def strip_file_extension(parameter) {
    return parameter.take(parameter.lastIndexOf('.'))
}

def get_file_extension(parameter) {
    return parameter.substring(parameter.lastIndexOf('.') + 1)
}

def update_site_values_with_multiple_files() {
    String file_names_string = env.SITE_VALUES_OVERRIDE_FILE_NAME;
    def file_names_array = file_names_string.split(',')

    for( String file_entry : file_names_array ) {
        def file_name_and_extension = file_entry.split('\\.')
        env.DATAFILE_NAME=file_name_and_extension[0]
        env.DATAFILE_TYPE=file_name_and_extension[1]
        env.PATH_TO_SITE_VALUES_OVERRIDE_FILE=file_entry
        sh "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml ost_bucket:set-bucket-name ost_bucket:set-datafile-name ost_bucket:set-output-dir ost_bucket:download-files-by-name-in-ost-bucket override-site-values:override-site-values"
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
