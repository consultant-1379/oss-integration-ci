#!/usr/bin/env groovy
import org.jenkins.plugins.lockableresources.LockableResourcesManager;

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.JENKINS_AGENT
    }
    parameters {
        string(name: 'ENV_NAME',
                description: 'Name of the Environment to be quarantined')
        string(name: 'JENKINS_AGENT',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the Jenkins agent label that you want the job to run on')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    stages {
        stage('Quarantine Environment') {
            steps {
                script {
                    quarantineEnvDetails()
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

def quarantineEnvDetails() {
    //Get all registered environments
    def manager = org.jenkins.plugins.lockableresources.LockableResourcesManager.get()
    //Set input paramaters as groovy variables
    def envName = params.ENV_NAME
    // Check is the environment reserved
    if ( manager.fromName(envName)?.isReserved() ) {
        // Quarantine the environment
        def description = manager.fromName(envName).getReservedBy()
        def newDescription
        if ( description.contains("Quarantined") ) {
            newDescription = description
        }
        else {
            newDescription = "Quarantined :: ${description}"
        }
        manager.reset([ manager.fromName(envName) ])
        manager.reserve([ manager.fromName(envName) ], "${newDescription}" )
        // Add a description to the jenkins Build Description
        currentBuild.description = "Quarantined ${envName}"
    }
    else {
        currentBuild.description = "Unreserved or Not Found :: ${envName}"
    }
}
