#!/usr/bin/env groovy

/* Comparing the chart version with the version in a particular version of the helmfile.
 *
 * DESCRIPTION:
 * If the helmfile includes an identical or later version of the chart(s), validation will fail.
 * The results are written to 'comparison_result.properties' file.
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'CHART_NAME',
                defaultValue: 'eric-cloud-native-base',
                description: 'Name of the Application Chart.' )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'ciloopman-docker-auth-config',
            description: 'ARM Docker secret'
        )
        string(name: 'CHART_VERSION',
                defaultValue: '0.0.0',
                description: 'The version of the Chart.' )
        string(name: 'CHART_REPO',
                defaultValue: '',
                description: 'The repository url of the Chart.')
        string(name: 'INT_CHART_VERSION',
                description: 'The version of helmfile' )
        string(name: 'INT_CHART_NAME',
                defaultValue: 'eric-eiae-helmfile',
                description: 'Helmfile Name' )
        string(name: 'INT_CHART_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
                description: 'Helmfile Repo' )
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
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'PATH_TO_HELMFILE',
                defaultValue: 'eric-eiae-helmfile/helmfile.yaml',
                description: 'Path to the helmfile')
        string(name: 'STATE_VALUES_FILE',
                defaultValue: 'eric-eiae-helmfile/build-environment/tags_true.yaml',
                description: 'Path to populated site-values file')
        string(name: 'CI_DOCKER_IMAGE',
            defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }

    stages {
        stage('Set build name') {
            steps {
                script{
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${params.CHART_NAME} ${params.CHART_VERSION}"
                }
            }
        }
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
        stage('Get Helmfile and extract') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} fetch-helmfile untar-and-copy-helmfile-to-workdir"
                }
            }
        }
        stage('Get Application Version and save to artifact.properties') {
            steps {
                sh "${bob} helmfile-details:get-version-details"
            }
        }
        stage('Comparing versions and writing results to comparison_result.properties') {
            steps {
                script{

                    def result = 'pass'
                    def chartsList = params.CHART_NAME.replaceAll('\\s', '').tokenize(',')
                    def versionsList = params.CHART_VERSION.replaceAll('\\s', '').tokenize(',')
                    def repoList = params.CHART_REPO.replaceAll('\\s', '').tokenize(',')
                    // def chartsMap = [chartsList, versionsList].transpose().collectEntries()
                    def passedChartNames = []
                    def passedChartVersions = []
                    def passedChartRepos = []

                    if(chartsList.size() > 0){ // In case of empty chart-name param

                        for (int i = 0; i < chartsList.size(); i++){
                            chartName = chartsList[i]
                            chartVersion = versionsList[i]
                            chartRepo = repoList[i]
                            chartVersionInHelmfile = getChartVersion(chartName, "${WORKSPACE}/artifact.properties")

                            // Skip comparison if a chart is not in the helmfile
                            if( !chartVersionInHelmfile ){
                                println("The '${chartName}' was not found in the helmfile. Comparison will be skipped");
                                continue
                            }

                            resultInInt = versionComparator(chartVersion, chartVersionInHelmfile)
                            chartResult = isVersionValid(resultInInt)

                            println "INFO: ${chartName} chart version checking ..."

                            sh "echo '${chartName}_version=${chartVersion}' >> comparison_result.properties"
                            sh "echo '${chartName}_in-helmfile=${chartVersionInHelmfile}' >> comparison_result.properties"
                            sh "echo '${chartName}=${chartResult}' >> comparison_result.properties"
                            if ( chartResult == 'pass' ){
                                passedChartNames.add(chartName)
                                passedChartVersions.add(chartVersion)
                                passedChartRepos.add(chartRepo)
                            }
                        }

                        if(passedChartNames.size() < 1){
                            result = 'failed'
                        }
                    }

                    sh "echo 'result=${result}' >> comparison_result.properties"
                    sh "echo 'PassedChartNames='${passedChartNames.join(', ')}'' >> comparison_result.properties"
                    sh "echo 'PassedChartVersions='${passedChartVersions.join(', ')}'' >> comparison_result.properties"
                    sh "echo 'PassedChartRepos='${passedChartRepos.join(', ')}'' >> comparison_result.properties"
                    currentBuild.description = "The chart(s) version validation status: " + result.toUpperCase()
                }
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'comparison_result.properties, artifact.properties', allowEmptyArchive: true, fingerprint: true
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

def get_ci_docker_image_url(ci_docker_image) {
    if (ci_docker_image.contains("default")) {
        String latest_ci_version = readFile "VERSION_PREFIX"
        String trimmed_ci_version = latest_ci_version.trim()
        url = ci_docker_image.split(':');
        return url[0] + ":" + trimmed_ci_version;
    }
    return ci_docker_image
}

def getChartVersion(chartName, file) {
    def filePath = readFile file
    def lines = filePath.readLines()
    for (line in lines) {
        if (line.contains(chartName)) {
            println "${line}"
            targetLine = line.split('=')
            return "${targetLine[1]}"
        }
    }
}

def versionComparator(chartVersion, releasedVersion){
    def VALID_TOKENS = /._-+/
    a = chartVersion.tokenize(VALID_TOKENS)
    b = releasedVersion.tokenize(VALID_TOKENS)

    for (i in 0..<Math.max(a.size(), b.size())) {

        if (i == a.size()) {
            return b[i].isInteger() ? -1 : 1
        } else if (i == b.size()) {
            return a[i].isInteger() ? 1 : -1
        }

        if (a[i].isInteger() && b[i].isInteger()) {
            int c = (a[i] as int) <=> (b[i] as int)
            if (c != 0) {
                return c
            }
        } else if (a[i].isInteger()) {
            return 1
        } else if (b[i].isInteger()) {
            return -1
        } else {
            int c = a[i] <=> b[i]
            if (c != 0) {
                return c
            }
        }
    }
  return 0
}

def isVersionValid(result) {
      int i = result
      switch(i) {
         case -1:
            println("Helmfile already contains a later version of the chart")
            return "failed"
         case 0:
            println("Helmfile already contains the same version of the chart")
            return "failed"
         case 1:
            println("Chart version is valid for helmfile upgrade");
            return "pass"
         default:
            println("The chart version is unknown");
            error("Abort the build.")
      }
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