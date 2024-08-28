def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label 'evo_docker_engine_gic'
    }
    options {
        timeout(time: env.TIMEOUT, unit: 'MINUTES')
    }
    parameters {
        string(name: 'KUBECONFIG', description: 'KUBECONFIG')
        string(name: 'NAMESPACE', defaultValue: 'cm-deploy', description: 'NAMESPACE')
        string(name: 'TIMEOUT', defaultValue: '30', description: 'execution timeout in mins')
        string(name: 'SUBMODULE_SYNC_TIMEOUT', defaultValue: '60', description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT', defaultValue: '300', description: 'Number of seconds before the submodule update command times out')
    }
    stages {
        stage('Clean Workspace') {
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Run the script') {
            steps {
                script {
                  withCredentials( [file(credentialsId: env.KUBECONFIG, variable: 'KUBECONFIG')]) {
                   sh "install -m 600 ${KUBECONFIG} ./admin.conf"
                   sh "${bob} eo-cm-onboarding-check"
                   }
                }
            }
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