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
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(
            name: 'FLOW_AREA' ,
            defaultValue: 'default' ,
            description: 'Refers to product deployment area. Eg:- eiapaas, release, productstaging, etc...'
        )
        string(
            name: 'PLATFORM_TYPE',
            defaultValue: 'default',
            description: 'The platform type of the environment. Eg:-Azure, AWS, GCP, CCD, EWS, etc..'
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
           name: 'DEPLOYMENT_MANAGER_DOCKER_IMAGE',
           defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:default',
           description: 'The full image url and tag for the deployment manager to use for the deployment. If the tag is set to default the deployment manager details will be fetched from the dm_version.yaml file from within the helmfile tar file under test'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
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
            name: 'TAGS',
            defaultValue: 'so pf uds adc th dmm eas',
            description: 'List of tags for applications that have to be deployed, e.g: so adc pf'
        )
        string(
            name: 'LA_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Log Aggregator'
        )
        string(
            name: 'IAM_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for IAM'
        )
        string(
            name: 'SO_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for SO'
        )
        string(
            name: 'UDS_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for UDS'
        )
        string(
            name: 'PF_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for PF'
        )
        string(
            name: 'GAS_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for GAS'
        )
        string(
            name: 'ADC_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for ADC'
        )
        string(
            name: 'APPMGR_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Application Manager'
        )
        string(
            name: 'TA_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Task Automation'
        )
        string(
            name: 'EAS_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Ericsson Adaptation Support'
        )
        string(
            name: 'CH_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Configuration Handling'
        )
        string(
            name: 'TH_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Topology Handling'
        )
        string(
            name: 'OS_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Oran Support'
        )
        string(
            name: 'VNFM_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EO EVNFM'
        )
        string(
            name: 'VNFM_REGISTRY_HOSTNAME',
            defaultValue: 'default',
            description: 'Registry Hostname for EO EVNFM'
        )
        string(
            name: 'GR_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EO GR'
        )
        string(
            name: 'ML_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Machine Learning(ML) Application'
        )
        string(
            name: 'AVIZ_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Assurance Visualization Application'
        )
        string(
            name: 'EO_CM_HOSTNAME',
            defaultValue: 'default',
            description: 'EO_CM_HOSTNAME'
        )
        string(
            name: 'HELM_REGISTRY_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EO HELM Registry'
        )
        string(
            name: 'VNFLCM_SERVICE_DEPLOY',
            defaultValue: 'false',
            description: 'EO VM VNFM Deploy, set \"true\" or \"false\"'
        )
        string(
            name: 'HELM_REGISTRY_DEPLOY',
            defaultValue: 'false',
            description: 'EO HELM Registry Deploy, set \"true\" or \"false\"'
        )
        string(
            name: 'IDUN_USER_SECRET',
            defaultValue: 'idun_credentials',
            description: 'Jenkins secret ID for default IDUN user password'
        )
        string(
            name: 'PATH_TO_AWS_FILES',
            defaultValue: 'NONE',
            description: 'Path within the Repo to the location of the Idun aaS AWS credentials and config directory'
        )
        string(
            name: 'AWS_ECR_TOKEN',
            defaultValue: 'NONE',
            description: 'AWS ECR token for aws public environments for Idun aaS'
        )
        string(
            name: 'FULL_PATH_TO_SITE_VALUES_FILE',
            description: 'Full path within the Repo to the site_values.yaml file'
        )
        string(
            name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
            defaultValue: 'NONE',
            description: 'Path within the Repo to the location of the site values override file(s). Content will override the content for the site values set in the FULL_PATH_TO_SITE_VALUES_FILE paramater.  Use CSV format for more than 1 override file'
        )
        string(
            name: 'PATH_TO_CERTIFICATES_FILES',
            description: 'Path within the Repo to the location of the certificates directory',
            trim: true
        )
        string(
            name: 'NAMESPACE',
            description: 'Namespace to install the Chart'
        )
        string(
            name: 'KUBECONFIG_FILE',
            description: 'Kubernetes configuration file to specify which environment to install on'
        )
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: 'ciloopman-user-creds',
            description: 'Jenkins secret ID for ARM Registry Credentials'
        )
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on'
        )
        string(
            name: 'WHAT_CHANGED',
            defaultValue: 'None',
            description: 'Variable to store what chart contains the change'
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
            name: 'DOWNLOAD_CSARS',
            defaultValue: 'false',
            description: 'When set to true the script will try to download the officially Released CSARs relation to the version of the applications within the helmfile being deployed.'
        )
        string(
            name: 'CRD_NAMESPACE',
            defaultValue: 'crd-namespace',
            description: 'Namespace which was used to deploy the CRD'
        )
        string(
            name: 'DEPLOY_ALL_CRDS',
            defaultValue: 'false',
            description: 'Used within CI when deploying multiple deployments in the one cluster. When set to true ensures all tagged CRDs are set to true, to ensure no dependency mismatch between deployments'
        )
        string(
            name: 'IPV6_ENABLE',
            defaultValue: 'false',
            description: 'Used to enable IPV6 within the site values file when set to true'
        )
        string(
            name: 'INGRESS_IP',
            defaultValue: 'default',
            description: 'INGRESS IP'
        )
        string(
            name: 'INGRESS_CLASS',
            defaultValue: 'default',
            description: 'ICCR ingress class name'
        )
        string(
            name: 'VNFLCM_SERVICE_IP',
            defaultValue: '0.0.0.0',
            description: 'LB IP for the VNF LCM service'
        )
        string(
            name: 'EO_CM_IP',
            defaultValue: 'default',
            description: 'EO CM IP'
        )
        string(
            name: 'EO_CM_ESA_IP',
            defaultValue: 'default',
            description: 'EO CM ESA IP'
        )
        string(
            name: 'FH_SNMP_ALARM_IP',
            defaultValue: 'default',
            description: 'LB IP for FH SNMP Alarm Provider'
        )
        string(
            name: 'USE_DM_PREPARE',
            defaultValue: 'false',
            description: 'Set to true to use the Deploymet Manager function \"prepare\" to generate the site values file'
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
            name: 'ENV_CONFIG_FILE',
            defaultValue: 'default',
            description: 'Can be used to specify the environment configuration file which has specific details only for the environment under test'
        )
        string(
            name: 'DDP_AUTO_UPLOAD',
            defaultValue: 'false',
            description: 'Set it to true when enabling the DDP auto upload and also need to add the DDP instance details into ENV_CONFIG_FILE and SITE_VALUES_OVERRIDE_FILE'
        )
        string(
            name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows'
        )
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
        string(
            name: 'VERBOSITY',
            defaultValue: '3',
            description: 'Verbosity can be from 0 to 4. Default is 3. Set to 4 if debug needed'
        )
        string(
            name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out'
        )
        string(
            name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out'
        )
    }
    environment {
        USE_TAGS = 'true'
        STATE_VALUES_FILE = "site_values_${params.INT_CHART_VERSION}.yaml"
        CSAR_STORAGE_URL = get_csar_storage_url("${params.CI_DOCKER_IMAGE}")
        CSAR_STORAGE_API_URL = get_csar_storage_api_url("${params.CI_DOCKER_IMAGE}")
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        PATH_TO_HELMFILE = "${params.INT_CHART_NAME}/helmfile.yaml"
        CSAR_STORAGE_INSTANCE = 'arm.seli.gic.ericsson.se'
        CSAR_STORAGE_REPO = 'proj-eric-oss-drop-generic-local'
        FETCH_CHARTS = 'true'
        HELMFILE_CHART_NAME = "${params.INT_CHART_NAME}"
        HELMFILE_CHART_VERSION = "${params.INT_CHART_VERSION}"
        HELMFILE_CHART_REPO = "${params.INT_CHART_REPO}"
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${params.NAMESPACE} ${params.KUBECONFIG_FILE.split("-|_")[0]}"
                }
            }
        }
        stage('Prepare') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
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
                            sh "${bob} helmfile:fetch-helmfile"
                            RETRY_ATTEMPT = 1
                        }
                    }
                }
            }
        }
        stage('Set Deployment Manager Version') {
            steps {
                sh "${bob} helmfile:extract-helmfile helmfile:get-dm-full-url-version"
                script {
                    env.DEPLOYMENT_MANAGER_DOCKER_IMAGE = sh (
                        script: "cat IMAGE_DETAILS.txt | grep ^IMAGE | sed 's/.*=//'",
                        returnStdout: true
                    ).trim()
                }
            }
        }
        stage('Prepare Working Directory') {
            steps {
                sh "${bob} untar-and-copy-helmfile-to-workdir fetch-site-values"
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
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
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
                            sh "${bob} update-site-values:substitute-ipv6-enable"
                            sh "${bob} update-site-values:substitute-application-hosts"
                            sh "${bob} update-site-values:substitute-application-deployment-option"
                            sh "${bob} update-site-values:substitute-application-service-option"
                            sh "${bob} update-repositories-file"
                            RETRY_ATTEMPT = 1
                        }
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

                        sh "${bob} get-release-details-from-helmfile"
                        sh "${bob} helmfile-charts-mini-csar-build"
                        sh "${bob} cleanup-charts-mini-csar-build"
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
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'), file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh "${bob} helmfile-details:get-version-details"
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
                stage ('Copy Certs and Kube Config') {
                    steps {
                        withCredentials([file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                            sh "${bob} copy-certificate-files"
                            sh 'install -m 600 ${KUBECONFIG} ./kube_config/config'
                        }
                    }
                }
                stage('Prepare Site Values using DM') {
                    when {
                        environment ignoreCase: true, name: 'USE_DM_PREPARE', value: 'true'
                    }
                    steps {
                        withAWS(credentials: 'esoa-aws-credentials', region: 'eu-west-1') {
                            retry(count: 5){
                                script{
                                    if (RETRY_ATTEMPT > 1) {
                                        echo "Rerunning the \"Prepare Site Values using DM'\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                                        sleep(180)
                                    }
                                    else {
                                        echo "Running the \"Prepare Site Values using DM'\" stage. Try ${RETRY_ATTEMPT} of 5"
                                    }
                                    RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                                    sh "${bob} prepare-site-values:rename-ci-site-values"

                                    if (params.PLATFORM_TYPE.toLowerCase() == "aws"){
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
                    environment ignoreCase: true, name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: 'NONE'
                }
            }
            steps {
                sh "${bob} override-site-values:override-site-values"
            }
        }
        stage('Update Site Values after Override') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-ipv6-enable"
                    sh "${bob} update-site-values:substitute-application-hosts"
                    sh "${bob} update-site-values:substitute-application-deployment-option"
                    sh "${bob} update-site-values:substitute-application-service-option"
                }
            }
        }
        stage('Update Site Values using key values from the environment configuration file') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-values-from-env-file"
                }
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
        stage ('Helmfile Deployment') {
            stages {
                stage ('Pre-Deployment Helmfile') {
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:remove-local-repositories-yaml"
                        sh "${bob} deploy-helmfile-using-deployment-manager:print-dm-version"
                        sh "${bob} deploy-helmfile-using-deployment-manager:archive-dm-version"
                    }
                }
                stage('Deploy Helmfile') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
                        }
                    }
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile"
                    }
                    post {
                        success {
                            sh "${bob} parse-log-file:parse-deployment-log"
                        }
                        always {
                            script {
                                if (params.FLOW_AREA.toLowerCase() == "eiapaas"){
                                    withCredentials([file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                                        sh 'install -m 600 ${KUBECONFIG} ./admin.conf'
                                    }
                                }
                            }
                        }
                        failure {
                            script {
                                withCredentials([file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                                    sh 'install -m 600 ${KUBECONFIG} ./admin.conf'
                                    if (params.COLLECT_LOGS.toLowerCase() == "true"){
                                        if (params.COLLECT_LOGS_WITH_DM.toLowerCase() == "true") {
                                            sh "${bob} gather-logs:gather-deployment-manager-logs || true"
                                        }
                                        else {
                                            sh "${bob} gather-logs:gather-adp-k8s-logs || true"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Deploy Helmfile AWS') {
                    when {
                        environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
                    }
                    steps {
                        script {
                            sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile-idunaas"
                        }
                    }
                    post {
                        always {
                            script {
                                if (params.FLOW_AREA.toLowerCase() == "eiapaas"){
                                    withCredentials([
                                        file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                                            sh 'install -m 600 ${KUBECONFIG} ./admin.conf'
                                    }
                                }
                            }
                        }
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
                                        sh "${bob} gather-logs:gather-adp-k8s-logs || true"
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
                    archiveArtifacts allowEmptyArchive: true, artifacts: "artifact.properties, logs_*.tgz, logs/*, ${env.STATE_VALUES_FILE}", fingerprint: true
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
                sh "${bob} git-clean"
            }
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