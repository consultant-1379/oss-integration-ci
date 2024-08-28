#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label 'Jenkins_evo_docker_engine_2'
    }
    parameters {
        string(name: 'INT_CHART_VERSION',
                description: 'The version of the base platform helmfile to build mini csars from' )
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'ciloopman-docker-auth-config',
                description: 'ARM Docker secret')
        string(name: 'ARM_API_TOKEN',
                defaultValue: 'eoadm100-arm-token',
                description: 'Jenkins secret ID for ARM Registry Credentials')
        string(name: 'FULL_PATH_TO_SITE_VALUES_FILE',
                defaultValue: 'site-values/eo/ci/site_values_helmfile-latest-populated.yaml',
                description: 'Full path within the Repo to the site_values.yaml file. Please choose the appropriate site values from the dropdown. Note EO has the eo directory reference.')
        string(name: 'INT_CHART_NAME',
                defaultValue: 'eric-eo-helmfile',
                description: 'Integration Chart Name. Please choose the appropriate repo from the dropdown.' )
        string(name: 'INT_CHART_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm/',
                description: 'Integration Chart Repo. Please choose the appropriate repo from the dropdown. Note EOs repo has reference to eo in the url' )
        string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
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
        string(name: 'GET_ALL_IMAGES',
                defaultValue: 'true',
                description: 'Set a true or false boolean to state whether to gather all release info independent of state values file')
        string(name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        STATE_VALUES_FILE = 'site_values_${env.INT_CHART_VERSION}.yaml'
        PATH_TO_HELMFILE = '${env.INT_CHART_NAME}/helmfile.yaml'
        INCLUDE_CHART_IMAGES = 'false'
        FETCH_CHARTS = 'true'
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Prepare') {
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
                }
            }
        }
        stage('Get latest PRA Common Base OS') {
            steps {
                script {
                    withCredentials([string(credentialsId: params.ARM_API_TOKEN, variable: 'TOKEN')]) {
                        def res = sh(script: """curl -ueoadm100:"${TOKEN}" -X POST https://arm.epk.ericsson.se/artifactory/api/search/aql -H "content-type: text/plain" -d 'items.find({ "repo": {"\044eq":"docker-v2-global-local"}, "path": {"\044match" : "proj-ldc/common_base_os_release/*"}}).sort({"\044desc": ["created"]}).limit(1)' 2>/dev/null | grep path""", returnStdout: true)
                        res = res.substring(res.lastIndexOf("/") + 1).replace(",","").replace("\"", "")
                        commonBaseOS = res
                    }

                    echo "Latest PRA Common Base OS Version : ${commonBaseOS}"

                    echo "Sending version to influxdb"
                    def commonBaseOSVersion = [:]
                    commonBaseOSVersion['latestCommonBaseOSVersion'] = "${commonBaseOS}"
                    influxDbPublisher(selectedTarget: 'grafana', customData: commonBaseOSVersion)

                }
            }
        }
        stage('Get Helmfile') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} fetch-helmfile"
                }
            }
        }
        stage('Prepare Working Directory'){
            steps {
                sh "${bob} untar-and-copy-helmfile-to-workdir fetch-site-values"
            }
        }
	    stage('Update repositories file') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                        sh "${bob} update-repositories-file"
                    }
                }
            }
        }
        stage('Pulling Charts') {
            steps {
                sh "${bob} get-release-details-from-helmfile"
            }
        }
        stage('Get Common Base OS Application Versions') {
            steps {
                script {
                    sh """ls -a | grep tgz | grep -v crd | grep -v helmfile | grep -v cloud | grep -v act-cna > listOfApplications.txt
                    while read p; do
                        helm template \044p --values ./site_values.yaml | grep 'image:' | grep -v cnom | sort -u >> images.txt
                    done <listOfApplications.txt
                    """
                    sh"""
                    sed -i 's/\r\$//g' images.txt
                    """
                     def versions = sh(script: """while read p; do
                        if [[ \044p == *"arm"* ]]; then
                            image=\044(echo "\044p" | grep -o -P '(?<=image: ).*' | tr -d '"');
                            docker pull \044image
                            commonBaseOS=\044(docker inspect "\044image" | grep '\"common_base_os\"' | sort -u | tr -d '"' | tr -d ' ' | tr -d ',');
                            application=\044(echo "\044image" | rev | cut -d'/' -f1 | rev | sort -u);
                            if [[ -n "\044commonBaseOS" ]]; then
                                echo "\044application / \044commonBaseOS" >> applications.txt;
                            fi
                        fi
                        done <images.txt""", returnStdout: false)

                    env.WORKSPACE = pwd()
                    def applications = readFile "${env.WORKSPACE}/applications.txt"
                    applications = applications.readLines()

                    echo "Sending versions of each application to influxdb"

                    applications.each{
                        def version="$it".substring("$it".lastIndexOf("/") + 1)
                        def application="$it".substring(0, "$it".indexOf(":"))
                        echo "Application: ${application} :${version}"
                        def eachApplicationVersion = [:]
                        eachApplicationVersion["${application}"] = "${version}"
                        if(version.contains("${commonBaseOS}".replaceAll("\\s","").substring(0, "${commonBaseOS}".lastIndexOf(".")))) {
                            eachApplicationVersion["${application}_status"] = "80".toInteger()
                            influxDbPublisher(selectedTarget: 'grafana', customData: eachApplicationVersion)
                        }
                        else{
                            eachApplicationVersion["${application}_status"] = "0".toInteger()
                            influxDbPublisher(selectedTarget: 'grafana', customData: eachApplicationVersion)
                        }
                    }

                    echo "Sending eo-chart version to influxdb"
                    def eoChartVersion = [:]
                    eoChartVersion['eoChartVersion'] = "${params.INT_CHART_VERSION}"
                    influxDbPublisher(selectedTarget: 'grafana', customData: eoChartVersion)
                }
            }
        }
        stage('Archiving artifact') {
            steps {
                script {
                    archiveArtifacts 'applications.txt'
                    archiveArtifacts 'images.txt'
                    archiveArtifacts 'site_values.yaml'
                 }
            }
        }
        stage('Cleaning Directory') {
            steps {
                script {
                    echo "Cleaning directory"
                    sh """rm *.tgz
                        rm images.txt
                        rm applications.txt
                        rm listOfApplications.txt"""
                 }
            }
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