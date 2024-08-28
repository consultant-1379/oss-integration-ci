#!/usr/bin/env groovy

import org.jenkins.plugins.lockableresources.LockableResourcesManager;

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'ENV_NAME', description: 'Name of the Environment to be unreserved')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Specify the slave label that you want the job to run on')
        string(name: 'TIMEOUT', defaultValue: '3600', description: 'Time to wait in seconds before the job should timeout')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Unreserve Environment') {
            steps {
                script {
                    UnReserveEnvDetails()
                }
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

def UnReserveEnvDetails() {
    //Get all registered environments
    def manager = org.jenkins.plugins.lockableresources.LockableResourcesManager.get()
    //Set input paramaters as groovy variables
    def envName = params.ENV_NAME
    // Check is the environment reserved
    if ( manager.fromName(envName)?.isReserved() ) {
        // Reset the reserved environment
        manager.reset([ manager.fromName(envName) ])
        // Add a description to the jenkins Build Description
        currentBuild.description = "Unreserved ${envName}"
    }
    else {
        currentBuild.description = "Already Unreserved ${envName}"
    }
}
