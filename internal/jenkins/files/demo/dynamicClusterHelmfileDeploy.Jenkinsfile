#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 *   + c12a011-config-file (admin.config to access c12a011 cluster)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobInternal = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
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
           name: 'DEPLOYMENT_MANAGER_VERSION',
           defaultValue: 'latest',
           description: 'The version of the deployment manager'
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
            name: 'TAGS',
            defaultValue: 'so pf uds adc th dmm eas',
            description: 'List of tags for applications that have to be deployed, e.g: so adc pf'
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
            name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:latest',
            description: 'CI Docker image to use. Mainly used in CI Testing flows'
        )
        string(name: 'CLUSTER_ID',
            defaultValue: '',
            description: 'For internal CI testing. Unique identifier for dynamic cluster, usually the pipeline ID when invoked from Spinnaker'
        )
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
    }
    environment {
        USE_TAGS = 'true'
        STATE_VALUES_FILE = "site_values_${params.INT_CHART_VERSION}.yaml"
        CSAR_STORAGE_URL = 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/'
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
        stage('Set build name for dynamic cluster') {
            when {
                not {
                    environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                }
            }
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${params.NAMESPACE} ${params.CLUSTER_ID}"
                }
            }
        }
        stage('Set build name') {
            when {
                environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
            }
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
                sh 'git submodule update --init bob'
                sh "git submodule sync"
                sh "git submodule update --init --recursive --remote"
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
        stage('Get Helmfile') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} helmfile:fetch-helmfile"
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
                sh "${bob} update-crd-helmfile"
                sh "${bob} tar-helmfile-from-workdir"
            }
        }
        stage('Prepare Working Directory Idun aaS') {
            when {
                not {
                    environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                }
            }
            steps {
                sh "${bob} prepare-workdir:set-chart-version prepare-workdir:copy-aws-credentials"
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
                        not {
                            environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                        }
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
                    environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
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
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-ipv6-enable"
                    sh "${bob} update-site-values:substitute-application-hosts"
                    sh "${bob} update-site-values:substitute-application-deployment-option"
                    sh "${bob} update-site-values:substitute-application-service-option"
                    sh "${bob} update-repositories-file"
                }
            }
        }
        stage('Build CSARs') {
            when {
                environment ignoreCase: true, name: 'DOWNLOAD_CSARS', value: 'false'
            }
            steps {
                sh "${bob} get-release-details-from-helmfile"
                sh "${bob} helmfile-charts-mini-csar-build"
                sh "${bob} cleanup-charts-mini-csar-build"
            }
        }
        stage('Download CSARs') {
            when {
                allOf {
                    environment ignoreCase: true, name: 'DOWNLOAD_CSARS', value: 'true'
                    environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'), file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh "${bob} get-app-details-from-helmfile"
                    sh "${bob} check-for-existing-csar-in-repo"
                    sh "${bob} download-csar-to-workspace"
                }
            }
        }
        stage('Pre Deployment Manager Configuration') {
            stages {
                stage('Deployment Manager Init') {
                    when {
                        environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                    }
                    steps {
                        sh "${bob} deployment-manager-init:deployment-manager-init"
                    }
                }
                stage('Deployment Manager Init Idun aaS') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                        }
                    }
                    steps {
                        sh "${bob} deployment-manager-init:deployment-manager-init-idunaas"
                    }
                }
                stage ('Copy Kube Config for Dynamic Cluster') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                        }
                    }
                    steps {
                        withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                            sh "${bobInternal} get-dynamic-cluster"
                            sh 'cp ./admin.conf ./kube_config/config'
                        }
                    }
                }
                stage ('Copy Certs and Kube Config') {
                    when {
                        environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                    }
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
                        sh "${bob} prepare-site-values:rename-ci-site-values"
                        script {
                            if (params.PATH_TO_AWS_FILES.toLowerCase() == "none"){
                                sh "${bob} prepare-site-values:deployment-manager-prepare"
                            }
                            else {
                                sh "${bob} prepare-site-values:deployment-manager-prepare-idunaas"
                            }
                        }
                        sh "${bob} prepare-site-values:populate-prepare-dm-site-values"
                    }
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
                not {
                    environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: params.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD')]) {
                    sh "${bob} update-site-values:substitute-idun-credential"
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
                // Only for internal CI testing
                stage('Deploy Helmfile to Dynamic Cluster') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                        }
                    }
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile"
                    }
                    post {
                        success {
                            sh "${bob} parse-log-file:parse-deployment-log"
                        }
                        failure {
                            script {
                                sh 'cp ./kube_config/config ./admin.conf'
                                sh 'chmod 600 ./admin.conf'
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
                stage('Deploy Helmfile') {
                    when {
                        allOf {
                            environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                            environment ignoreCase: true, name: 'CLUSTER_ID', value: ''
                        }
                    }
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile"
                    }
                    post {
                        success {
                            sh "${bob} parse-log-file:parse-deployment-log"
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
                stage('Deploy Helmfile Idun aaS') {
                    when {
                        not {
                            environment ignoreCase: true, name: 'PATH_TO_AWS_FILES', value: 'NONE'
                        }
                    }
                    steps {
                        sh "${bob} deploy-helmfile-using-deployment-manager:deploy-helmfile-idunaas"
                    }
                    post {
                        always {
                            withCredentials([file(credentialsId: params.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                                sh 'install -m 600 ${KUBECONFIG} ./admin.conf'
                            }
                        }
                        success {
                            sh "${bob} annotate-namespace-installed-helmfile"
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
            }
        }
    }
}

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}
