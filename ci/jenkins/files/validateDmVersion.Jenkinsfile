#!/usr/bin/env groovy

/* Comparing the DM version with the version where skip flag was introduced.
 *
 * DESCRIPTION:
 * If the DM version is older then specified (1.43.53), USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES will be set to false.
 * The results are written to 'comparison_result.properties' file.
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'CURRENT_DM_VERSION',
                defaultValue: '0.0.0',
                description: 'Version of DM that is used'
        )
        string(name: 'MIN_VALID_DM_VERSION',
                defaultValue: '1.43.53',
                description: 'Lower version does not accept --skip-upgrade-for-unchanged-releases flag.'
        )
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
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
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'evo_docker_engine',
            description: 'Specify the slave label that you want the job to run on'
        )

    }

    environment {
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Set build name') {
            steps {
                script{
                    currentBuild.displayName = "${env.BUILD_NUMBER}"
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
        stage('Get Deployment Manager version'){
            steps{
                script{
                    sh "${bob} deploy-helmfile-using-deployment-manager:archive-dm-version"
                }
            }
        }
        stage('Comparing versions and writing results to comparison_result.properties') {
            steps {
                script{

                    def dm_vervion = readFile "${env.WORKSPACE}/artifact.properties"
                    def currentDmVersion = dm_vervion.tokenize('=').last()

                    println "Current DM Version is " + currentDmVersion

                    def result = 'false' //true
                    def minValidDmVersion = params.MIN_VALID_DM_VERSION

                    resultInInt = versionComparator(minValidDmVersion, currentDmVersion)
                    dmResult = isVersionValid(resultInInt)

                    result = dmResult

                    sh "echo 'USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES=${result}' >> comparison_result.properties"
                    sh "echo 'MIN_VALID_DM_VERSION=${params.MIN_VALID_DM_VERSION}' >> comparison_result.properties"
                    sh "echo 'CURRENT_DM_VERSION=${currentDmVersion}' >> comparison_result.properties"
                    currentBuild.description = "USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES: " + result.toUpperCase()
                }
            }
        }
    }
    post {
        always {
            script {
                if (getContext(hudson.FilePath)) {
                    archiveArtifacts artifacts: 'comparison_result.properties', allowEmptyArchive: true, fingerprint: true
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

def versionComparator(minValidDmVersion, currentDmVersion){
    def VALID_TOKENS = /._-+/
    b = minValidDmVersion.tokenize(VALID_TOKENS)
    a = currentDmVersion.tokenize(VALID_TOKENS)

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
            println("DM has old version, skip flag is NOT acceptable")
            return "false"
         case 0:
            println("DM has min required version for skip flag usage")
            return "true"
         case 1:
            println("DM version is higher and valid for skip flag usage");
            return "true"
         default:
            println("DM version is unknown");
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