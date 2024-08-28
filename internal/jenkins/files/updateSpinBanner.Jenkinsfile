#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

def bob = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    parameters {
        string(name: 'SPIN_CREDENTIALS',
                defaultValue: 'ossapps100-user-credentials',
                description: 'Jenkins secret ID with Spinnaker username and password')
        string(name: 'APP_LIST',
                defaultValue: '',
                description: 'Comma-separated list of applications.  Supports keyword using ALL_<keyword> format, eg. ALL_e2e-cicd')
        string(name: 'BANNER_TEXT',
                defaultValue: '',
                description: 'Banner text to update.  Supports markdown format, eg. [link text](http://url-goes-here)')
        choice(name: 'BG_COLOR',
                choices: ['success', 'warning', 'danger', 'accessory-light'],
                description: 'Banner background color')
        choice(name: 'TEXT_COLOR',
                choices: ['on-dark', 'secondary', 'caption'],
                description: 'Banner text color')
        choice(name: 'ENABLED',
                choices: ['true', 'false'],
                description: 'Banner enabled')
        choice(name: 'SKIP',
                choices: ['false', 'true'],
                description: 'Skip banner update (true is a dry-run)')
        choice(name: 'DELETE',
                choices: ['false', 'true'],
                description: 'If set to true, will try to delete a banner if matching text is found')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
        string(name: 'PIPELINE_MGT_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-dev/eric-oss-pipeline-mgt-scripts:latest',
                description: 'Pipeline-mgt CI image to use (set to "local" to build inline)')
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
                sh "git submodule sync"
                sh "git submodule update --init --recursive --remote"
                sh "${bob} git-clean"
            }
        }
        stage('Build Pipeline-Mgt Scripts Image') {
            when {
                environment ignoreCase: true, name: 'PIPELINE_MGT_DOCKER_IMAGE', value: 'local'
            }
            steps {
                sh "${bob} build-local-pipeline-mgt-image"
            }
        }
        stage('Sync Spinnaker Banners from CSV') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.SPIN_CREDENTIALS, usernameVariable: 'SPIN_USERNAME', passwordVariable: 'SPIN_PASSWORD')]) {
                        sh "${bob} add-global-banner"
                    }
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
