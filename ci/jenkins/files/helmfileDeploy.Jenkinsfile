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
def common_functions

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
            description: 'Refers to product deployment area. Eg:- eiapaas, release, productstaging, etc...'
        )
        string(
            name: 'PLATFORM_TYPE',
            defaultValue: 'default',
            description: 'The platform type of the environment. Eg:-Azure, AWS, GCP, CCD, EWS, openshift etc..'
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
            name: 'OPTIONAL_KEY_VALUE_LIST',
            defaultValue: 'None',
            description: 'Optional comma separated list of additional key/value pairs to be added to site values. Each key level should be separated by \'.\' and value by \'=\' , e.g. eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false'
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
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret'
        )
        string(
            name: 'SPINNAKER_PIPELINE_ID',
            defaultValue: '123456',
            description: 'ID for Spinnaker pipeline. Used as a placeholder to mitigate Jenkins 404 errors.'
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
            description: 'List of tags for applications that have to be deployed (e.g: so adc pf). Enter "None" into this field to leave all tags as false'
        )
        string(
            name: 'LA_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Log Aggregator'
        )
        string(
            name: 'KAFKA_BOOTSTRAP_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Kafka Bootstrap'
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
            name: 'GLOBAL_VNFM_REGISTRY_HOSTNAME',
            defaultValue: 'default',
            description: 'Global Registry Hostname for EO EVNFM'
        )
        string(
            name: 'GR_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EO GR'
        )
        string(
            name: 'GR_SECONDARY_HOSTNAME',
            defaultValue: 'default',
            description: 'Secondary Hostname for EO GR'
        )
        string(
            name: 'ML_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Machine Learning(ML) Application'
        )
        string(
            name: 'BDR_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for Bulk Data Repository (BDR) Application'
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
            name: 'EO_LM_HOSTNAME',
            defaultValue: 'default',
            description: 'EO_LM_HOSTNAME'
        )
        string(
            name: 'EO_LM_GIT_HOSTNAME',
            defaultValue: 'default',
            description: 'EO_LM_GIT_HOSTNAME'
        )
        string(
            name: 'EO_LM_OCI_HOSTNAME',
            defaultValue: 'default',
            description: 'EO_LM_OCI_HOSTNAME'
        )
        string(
            name: 'HELM_REGISTRY_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EO HELM Registry'
        )
        string(
            name: 'EIC_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for EIC'
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
            name: 'FUNCTIONAL_USER_TOKEN',
            defaultValue: 'NONE',
            description: 'Jenkins identity token for ARM Registry access'
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
            name: 'TIMEOUT',
            defaultValue: '3600',
            description: 'Time to wait in seconds before the job should timeout'
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
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
        COOKIE_DOMAIN = get_cookie_domain("${params.EIC_HOSTNAME}")
        CLUSTER_NAME = "${params.KUBECONFIG_FILE.split("-|_")[0]}"
    }
    stages {
        stage('==Parallel Stage 1=='){
            parallel{
                stage('Set build name') {
                    steps {
                        script {
                            currentBuild.displayName = "${env.BUILD_NUMBER} ${params.NAMESPACE} ${env.CLUSTER_NAME}"
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
                                common_functions = load('ci/jenkins/pipeline/functions/groovy/lib/common.groovy')
                                RETRY_ATTEMPT = common_functions.stage_start_retry("Prepare", RETRY_ATTEMPT, 180)

                                // Extract the submodules from the .gitmodules file
                                def submodules = get_submodules_list_from_gitmodules('.gitmodules')
                                echo "Submodule names: ${submodules}"

                                // The list of parameters that can determine the need for a submodule
                                def parameters_to_check = [params.PATH_TO_AWS_FILES, params.FULL_PATH_TO_SITE_VALUES_FILE,
                                params.PATH_TO_SITE_VALUES_OVERRIDE_FILE, params.PATH_TO_CERTIFICATES_FILES,
                                params.ENV_CONFIG_FILE]

                                // Checkout submodules
                                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                                for (submodule in submodules) {
                                    echo "Checking if $submodule is required"
                                    // Pass in the current submodule to check if needed, along with the list of parameters
                                    checkout_submodule_if_needed(submodule, parameters_to_check)
                                }
                                sh "${bob} git-clean"

                                RETRY_ATTEMPT = 1
                            }
                        }
                    }
                }
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    retry(count: 5){
                        script {
                            RETRY_ATTEMPT = common_functions.stage_start_retry("Install Docker Config", RETRY_ATTEMPT, 180)

                            withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                                sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                            }

                            RETRY_ATTEMPT = 1
                        }
                    }
                }
            }
        }
        stage('Get Helmfile') {
            steps {
                retry(count: 5){
                    script{
                        RETRY_ATTEMPT = common_functions.stage_start_retry("Get Helmfile", RETRY_ATTEMPT, 180)

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
        stage('==Parallel Stage 2=='){
            parallel{
                stage('Set Deployment Manager Version') {
                    steps {
                        script{
                            sh "${bob} helmfile:extract-helmfile helmfile:get-dm-full-url-version"

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
            }
        }
        stage('==Parallel Stage 3=='){
            parallel{
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
        stage('Override Site Values - CSAR Build') {
            when {
                not {
                    environment ignoreCase: true, name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: 'NONE'
                }
            }
            steps {
                sh "${bob} override-site-values:override-site-values"
            }
        }
        stage('Update Site Values') {
            steps {
                retry(count: 5){
                    script{
                        RETRY_ATTEMPT = common_functions.stage_start_retry("Update Site Values", RETRY_ATTEMPT, 180)

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
        stage('Enable/Disable Applications in Site Values - CSAR Build') {
            when {
                not {
                    environment ignoreCase: true, name: 'OPTIONAL_KEY_VALUE_LIST', value: 'NONE'
                }
            }
            steps {
                sh "${bob} modify-site-values:create-site-values-update"
                sh "${bob} modify-site-values:merge-site-values-update"
            }
        }
        stage('Build CSARs') {
            when {
                environment ignoreCase: true, name: 'DOWNLOAD_CSARS', value: 'false'
            }
            steps {
                retry(count: 5){
                    script{
                        RETRY_ATTEMPT = common_functions.stage_start_retry("Build CSARs", RETRY_ATTEMPT, 180)

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
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'), file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
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
                        retry(count: 5){
                            script {
                                RETRY_ATTEMPT = common_functions.stage_start_retry("Deployment Manager Init", RETRY_ATTEMPT, 180)

                                sh "${bob} deployment-manager-init:deployment-manager-init"

                                RETRY_ATTEMPT = 1
                            }
                        }
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
        stage('Enable/Disable Applications in Site Values - Deployment') {
            when {
                not {
                    environment ignoreCase: true, name: 'OPTIONAL_KEY_VALUE_LIST', value: 'NONE'
                }
            }
            steps {
                sh "${bob} modify-site-values:create-site-values-update"
                sh "${bob} modify-site-values:merge-site-values-update"
            }
        }
        stage('Openshift restricted SCC additions') {
            when {
               environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'openshift'
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
        stage('Record Server Event') {
            when {
                environment ignoreCase: true, name: 'INT_CHART_NAME', value: 'eric-eiae-helmfile'
            }
            steps {
                script {
                    sh "${bob} record-server-event:init-event-id record-server-event:get-server-event-variables record-server-event:write-api-url-variable record-server-event:write-gui-url-variable record-server-event:write-from-version-variable"
                    if (is_testware_secret_available()) {
                        sh "${bob} record-server-event:write-event-deployment-type record-server-event:write-event-description record-server-event:write-event-metadata record-server-event:record-server-event record-server-event:record-event-id record-server-event:write-event-id-to-properties"
                    } else {
                        echo "The API/GUI URL was not available in the testware-resources-secret. The server event will not be recorded..."
                    }
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
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-skip-image-push-parameter"
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-skip-upgrade-for-unchanged-releases-parameter"
                        sh "${bob} deploy-helmfile-using-deployment-manager:set-use-certm-parameter"
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

                            retry(count: 5){
                                script{
                                    RETRY_ATTEMPT = common_functions.stage_start_retry("Deploy Helmfile - post success", RETRY_ATTEMPT, 30)

                                    sh "${bob} get-charts-deployment-time:deployment-time-measurement"

                                    RETRY_ATTEMPT = 1
                                }
                            }

                            archiveArtifacts artifacts: "deploy-timing.yaml", allowEmptyArchive: true, fingerprint: true

                            script {
                                if (env.INT_CHART_NAME == "eric-eiae-helmfile") {
                                    if (is_testware_secret_available()) {
                                        String event_id = readFile ".bob/var.testware-event-id"
                                        if (event_id.trim() != "not_found") {
                                            sh "${bob} record-server-event:record-successful-deployment"
                                            sh "${bob} record-server-event:end-server-event"
                                        }
                                    }
                                }
                            }
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
                                            sh "${bob} gather-logs:gather-system-logs || true"
                                        }
                                    }
                                }
                                if (env.INT_CHART_NAME == "eric-eiae-helmfile") {
                                    if (is_testware_secret_available()) {
                                        sh "${bob} record-server-event:record-failed-deployment"
                                        sh "${bob} record-server-event:end-server-event"
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
                                    withCredentials([file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
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
                                        sh "${bob} gather-logs:gather-system-logs || true"
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
                sh "${bob} gather-logs:gather-system-logs || true"
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                    archiveArtifacts artifacts: "ci-script-executor-logs/*, **/system_logs_*.tgz", allowEmptyArchive: true, fingerprint: true
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

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}

def get_submodules_list_from_gitmodules(gitmodules_file) {
    def gitmodulesContent = readFile(gitmodules_file)
    def lines = gitmodulesContent.readLines()
    def submodules = []
    for (line in lines) {
        if (line.trim().startsWith("[submodule")) {
            def submodule = line.trim().split(' ')[1].replace('\"', '').replace(']', '')
            submodules.add(submodule)
        }
    }
    return submodules
}

def checkout_submodule_if_needed(submodule, list_of_parameters_to_check) {
    for (parameter in list_of_parameters_to_check) {
        if (parameter.startsWith(submodule) || submodule.equals("bob") || submodule.equals("eo-integration-ci")) {
            echo "Checking out submodule: $submodule"
            def command = "git submodule update --init --recursive --remote --depth=1 --jobs=5 " + submodule
            command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", command)
            break
        }
    }
}

def get_cookie_domain(String EIC_HOSTNAME) {
    if (EIC_HOSTNAME != "default"){
        return EIC_HOSTNAME.substring(EIC_HOSTNAME.indexOf(".") + 1)
    } else {
        return "default"
    }
}

def is_testware_secret_available(){
    String api_url = readFile ".bob/var.testware-api-url"
    String gui_url = readFile ".bob/var.testware-gui-url"
    return api_url.trim() != "not_found" || gui_url.trim() != "not_found"
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