#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review \${GERRIT_PATCHSET_REVISION}"
def verifications = [
        'Verified'      : -1
]


pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    parameters {
        string(name: 'APP_NAME',
                defaultValue: params.APP_NAME ?: '',
                description: 'application name in repo')
        string( name: 'CHART_PATH',
                defaultValue: params.CHART_PATH ?: '',
                description: 'Relative path to helm chart in git repo.')
        string( name: 'GIT_REPO_URL',
                defaultValue: params.GIT_REPO_URL ?: '',
                description: 'Gerrit https url to helm chart git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart')
        string( name: 'GERRIT_PROJECT',
                defaultValue: params.GERRIT_PROJECT ?: '',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base')
        string(name: 'PATH_TO_SITE_VALUES_FILE',
                defaultValue: params.PATH_TO_SITE_VALUES_FILE ?: 'testsuite/site_values.yaml',
                description: 'The path including file name of the site values file for templating the chart for the static test and design rule checking. The path should start from the root of the App chart repo')
        string(name: 'SCHEMA_TESTS_PATH',
                defaultValue: params.SCHEMA_TESTS_PATH ?: 'testsuite/schematests/tests',
                description: 'The path to the schema tests within the chart repo. Set to "NONE" to skip these tests')
        string(name: 'FULL_CHART_SCAN',
                defaultValue: params.FULL_CHART_SCAN ?: 'false',
                description: 'If "true" then with whole chart with its dependencies will be scanned in "prep"')
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: params.GERRIT_USER_SECRET ?: '',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: params.ARMDOCKER_USER_SECRET ?: '',
                description: 'Jenkins secret ID with ARM Docker config details')
        string(name: 'HELM_REPO_CREDENTIALS_ID',
                defaultValue: params.HELM_REPO_CREDENTIALS_ID ?: '',
                description: 'Repositories.yaml file credential used for auth')
        string(name: 'USE_ADP_ENABLER',
                defaultValue: params.USE_ADP_ENABLER ?: 'adp-cihelm',
                description: 'To use a specific adp enabler to build the chart, two options available, adp-cihelm or adp-inca. Default, adp-cihelm')
        string(name: 'PCR_MASTER_JOB_NAME',
                defaultValue: params.PCR_MASTER_JOB_NAME ?: 'OSS-Integration-Common-Testing',
                description: 'This is the master common pcr job that will be trigged by this job to execute the tests')
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
                defaultValue: params.SLAVE_LABEL ?: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'CI_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
}
    agent {
        label env.SLAVE_LABEL
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${BUILD_NUMBER} ${GERRIT_REFSPEC}"
                }
            }
        }
        stage('Cleaning Git Repo') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Starting PCR test') {
            steps {
                build job: env.PCR_MASTER_JOB_NAME,
                propagate: true,
                wait: true,
                parameters: [
                    string(name: 'GERRIT_USER_SECRET', value: env.GERRIT_USER_SECRET),
                    string(name: 'ARMDOCKER_USER_SECRET', value: env.ARMDOCKER_USER_SECRET),
                    string(name: 'APP_NAME', value: env.APP_NAME),
                    string(name: 'CHART_PATH', value: env.CHART_PATH),
                    string(name: 'HELM_REPO_CREDENTIALS_ID', value: env.HELM_REPO_CREDENTIALS_ID),
                    string(name: 'GIT_REPO_URL', value: env.GIT_REPO_URL),
                    string(name: 'GERRIT_PROJECT', value: env.GERRIT_PROJECT),
                    string(name: 'SCHEMA_TESTS_PATH', value: env.SCHEMA_TESTS_PATH),
                    string(name: 'PATH_TO_SITE_VALUES_FILE', value: env.PATH_TO_SITE_VALUES_FILE),
                    string(name: 'GERRIT_REFSPEC', value: env.GERRIT_REFSPEC),
                    string(name: 'GERRIT_PATCHSET_REVISION', value: env.GERRIT_PATCHSET_REVISION),
                    string(name: 'VCS_BRANCH', value: env.GERRIT_BRANCH),
                    string(name: 'HELM_REPO_API_TOKEN', value: ''),
                    string(name: 'FULL_CHART_SCAN', value: env.FULL_CHART_SCAN),
                    string(name: 'SLAVE_LABEL', value: env.SLAVE_LABEL)
                ]
            }
        }

    }
    post {
        success {
            script {
                verifications['Verified'] = +1
                def labelArgs = verifications
                .collect { entry -> "--label ${entry.key}=${entry.value}" }
                .join(' ')
                sh "${gerritReviewCommand} ${labelArgs}"
            }
        }
        failure {
            script {
                def labelArgs = verifications
                .collect { entry -> "--label ${entry.key}=${entry.value}" }
                .join(' ')
                sh "${gerritReviewCommand} ${labelArgs}"
            }
        }
        cleanup {
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
