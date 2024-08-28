#!/usr/bin/env groovy

def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review --message '\"${Message}\"' ${LABEL} \${GERRIT_CHANGE_NUMBER},\${GERRIT_PATCHSET_NUMBER}"

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'Message', description: 'A message to be added as feedback on the triggering Gerrit event.')
        string(name: 'LABEL',
                defaultValue: '',
                description: 'A verification label used in the event of the test flow failing.')
        string(name: 'GERRIT_CHANGE_NUMBER')
        string(name: 'GERRIT_PATCHSET_NUMBER')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Specify the slave label that you want the job to run on')
        string(name: 'TIMEOUT', defaultValue: '3600', description: 'Time to wait in seconds before the job should timeout')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Comment on Gerrit') {
            steps {
                sh "${gerritReviewCommand}"
            }
        }
    }
    post {
        failure {
            script {
                if (getContext(hudson.FilePath)) {
                    sh "printenv | sort"
                }
            }
        }
        cleanup {
            cleanWs()
        }
    }
}
