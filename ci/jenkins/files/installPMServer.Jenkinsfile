#!/usr/bin/env groovy



def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'NAMESPACE',
            defaultValue: 'appstaging-monitoring',
            description: 'Namespace to install eric-pm-server within')
        string(name: 'INGRESS_IP',
            defaultValue: 'prometheus.metricstest.hart109.rnd.gic.ericsson.se',
            description: 'Ingress name to access prometheus e.g prometheus.metrics.hart109.rnd.gic.ericsson.se')
        string(name: 'TEARDOWN',
            defaultValue: 'false',
            description: 'Option to completely uninstall prometheus and all associated resources, caution when changing, completely uninstalls whn set to true')
        string(name: 'GRAFANA_HOSTNAME',
            defaultValue: 'http://seliius29510.seli.gic.ericsson.se:3000/',
            description: 'Hostname of the Grafana instance to be used, App Staging Grafana by default')
        string(name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on')
        string(name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
        string(name: 'KUBECONFIG_FILE',
            defaultValue: 'hart109-admin-config',
            description: 'Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST.')
        string(name: 'ENV_FILES_BUCKET_NAME',
            defaultValue: 'None',
            description: 'Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST.')
        string(name: 'GRAFANA_DATASOURCE_NAME',
            defaultValue: 'clustername-Prometheus',
            description: 'Name of data source to be added to Grafana, e.g hart109-Prometheus')
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: 'ciloopman-user-creds',
            description: 'Jenkins secret ID for helm Credentials')
        string(
            name: 'GRAFANA_API_SECRET',
            defaultValue: 'grafana-api-key-as',
            description: 'Jenkins secret ID for Grafana Api'
        )
        string(
            name: 'PMSERVER_PVC_SIZE',
            defaultValue: '20',
            description: 'PVC size in Gi for eric-pm-server'
        )
        string(
            name: 'PMSERVER_MEMORY_LIMITS',
            defaultValue: '10',
            description: 'Memory limits in Gi for eric-pm-server'
        )
        string(
            name: 'REGISTRY_SECRET_NAME',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret'
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
    stages {
        stage('Set Build Name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${NAMESPACE} ${KUBECONFIG_FILE.split("-|_")[0]}"
                }
            }
        }
        stage('Clean Workspace') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
                //Initialize parameters as environment variables due to https://issues.jenkins-ci.org/browse/JENKINS-41929
                evaluate """${def script = ""; params.each { k, v -> script += "env.${k} = '''${v}'''\n" }; return script}"""
            }
        }
        stage ('Fetch Kube Config using OST') {
            when {
                not {
                    environment ignoreCase:true, name: 'ENV_FILES_BUCKET_NAME', value: 'none'
                }
            }
            environment {
                BUCKET_NAME = "${params.ENV_FILES_BUCKET_NAME}"
                BUCKET_OUTPUT_DIR = "."
            }
            steps {
                withCredentials([usernamePassword(credentialsId:params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} ost_bucket:set-bucket-name ost_bucket:set-output-dir ost_bucket:download-all-files-in-ost-bucket"
                    sh "mv ./${env.KUBECONFIG_FILE} ./admin.conf"
                    sh "chmod 600 ./admin.conf"
                }
            }
        }
        stage('Fetch Kube Config From Jenkins Credentials') {
            when {
                environment ignoreCase:true, name: 'ENV_FILES_BUCKET_NAME', value: 'none'
            }
            steps {
                withCredentials( [file(credentialsId:env.KUBECONFIG_FILE, variable: 'KUBECONFIG')]) {
                    sh "install -m 600 ${KUBECONFIG} ./admin.conf"
                }
            }
        }
        stage('Prometheus Installation') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'), string(credentialsId: params.GRAFANA_API_SECRET, variable: 'GRAFANA_API_KEY'), file(credentialsId: params.REGISTRY_SECRET_NAME, variable: 'REGISTRY_SECRET_NAME')]) {
                    sh "install -m 600 ${REGISTRY_SECRET_NAME} ./armdockerconfig.json"
                    sh "chmod +x ${env.WORKSPACE}/ci/jenkins/scripts/pm-server-installation.sh"
                    sh "${bob} pm-server-installation"
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
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
