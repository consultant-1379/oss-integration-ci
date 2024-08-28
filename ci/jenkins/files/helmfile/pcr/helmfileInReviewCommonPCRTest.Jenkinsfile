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
        string( name: 'CHART_PATH',
                defaultValue: params.CHART_PATH ?: '',
                description: 'Relative path to helmfile local chart in git repo.')
         string( name: 'KUBEVAL_KINDS_TO_SKIP',
                 defaultValue: params.KUBEVAL_KINDS_TO_SKIP ?: '',
                 description: 'Skipped Kubeval checks for specific kinds.')
        string( name: 'GERRIT_PROJECT',
                defaultValue: params.GERRIT_PROJECT ?: '',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss.eiae/eiae-helmfile')
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: params.GERRIT_USER_SECRET ?: '',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: params.ARMDOCKER_USER_SECRET ?: '',
                description: 'Jenkins secret ID with ARM Docker config details')
        string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: params.FUNCTIONAL_USER_SECRET ?: '',
                description: 'Jenkins secret ID with ARM Docker config details')
        string(name: 'PCR_MASTER_JOB_NAME',
                defaultValue: params.PCR_MASTER_JOB_NAME ?: 'OSS-Integration-Helmfile-Common-Testing',
                description: 'This is the master common pcr job that will be triggered by this job to execute the tests')
        string(name: 'PATH_TO_SITE_VALUES_FILE',
                defaultValue: params.PATH_TO_SITE_VALUES_FILE ?: '',
                description: 'The full path to the ci site values template file for the Helmfile under test')
        string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
                defaultValue: params.PATH_TO_SITE_VALUES_OVERRIDE_FILE ?: '',
                description: 'The full path to the ci site values override template file for the additional values needed for the Helmfile under test')
        string( name: 'KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH',
                defaultValue: params.KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH ?: '',
                description: 'The full path to the kubernetes compatibility site values file used during the Kubernetes Testing Phase')
        string(name: 'HELMFILE_NAME',
                defaultValue: params.HELMFILE_NAME ?: '',
                description: 'The name of the Helmfile under test e.g. eiae-helmfile/eo-helmfile. Very important as it is used to set the build name and conditionally run certain Helmfile-specific stages')
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
                    string(name: 'FUNCTIONAL_USER_SECRET', value: env.FUNCTIONAL_USER_SECRET),
                    string(name: 'CHART_PATH', value: env.CHART_PATH),
                    string(name: 'KUBEVAL_KINDS_TO_SKIP', value: env.KUBEVAL_KINDS_TO_SKIP),
                    string(name: 'GERRIT_PROJECT', value: env.GERRIT_PROJECT),
                    string(name: 'GERRIT_REFSPEC', value: env.GERRIT_REFSPEC),
                    string(name: 'GERRIT_PATCHSET_REVISION', value: env.GERRIT_PATCHSET_REVISION),
                    string(name: 'VCS_BRANCH', value: env.GERRIT_BRANCH),
                    string(name: 'PATH_TO_SITE_VALUES_FILE', value: env.PATH_TO_SITE_VALUES_FILE),
                    string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: env.PATH_TO_SITE_VALUES_OVERRIDE_FILE),
                    string(name: 'KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH', value: env.KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH),
                    string(name: 'HELMFILE_NAME', value: env.HELMFILE_NAME),
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