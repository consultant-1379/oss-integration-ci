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
        choice( name: 'DEV_OR_PUBLISH',
                choices: "dev\npublish\n",
                description: '''dev :: Generate a dev version of the CI/CD Docker image\n
                                publish :: Officially release the CI/CD Docker Image''')
        string(name: 'GERRIT_PROJECT',
                defaultValue: 'OSS/com.ericsson.oss.aeonic/oss-integration-ci',
                description: 'Gerrit project details e.g. OSS/com.ericsson.oss.aeonic/oss-integration-ci')
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'eoadm100-user-credentials',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'GERRIT_REFSPEC',
                description: 'Ref spec of the review under test')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'eoadm100-docker-auth-config',
                description: 'ARM Docker secret')
        string(name: 'GERRIT_PATCHSET_NUMBER',
                defaultValue: 'default',
                description: 'Gerrit Patchset Number from the review')
        string(name: 'GERRIT_CHANGE_NUMBER',
                defaultValue: '99999999',
                description: 'Gerrit change number from the review used to set a unique version for dev testing')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'The amount of time to wait in seconds for all the submodules to clone when executing the \"gerrit clone\" command')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'GERRIT_REFSPEC_CI',
                defaultValue: 'refs/heads/master',
                description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **')
    }
    environment {
        NEXT_GERRIT_PATCHSET_NUMBER = step_patch_set("${GERRIT_PATCHSET_NUMBER}")
        NEXT_GERRIT_REFSPEC = "${GERRIT_REFSPEC}"
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
                sh "git submodule update --init --recursive --remote --depth=1 --jobs=5 bob"
                sh "${bob} git-clean"
            }
        }
        stage('Rebase review if needed') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        def rebase_output = sh (
                            script: "${bob} gerrit:rebase-review-if-not-mergeable",
                            returnStdout: true
                        ).trim()
                        echo "${rebase_output}"
                        if (rebase_output.contains("\"mergeable\":false")) {
                            NEXT_GERRIT_REFSPEC = step_gerrit_refspec_patch_number("${GERRIT_REFSPEC}")
                            NEXT_GERRIT_PATCHSET_NUMBER = step_patch_set("${NEXT_GERRIT_PATCHSET_NUMBER}")
                        }
                    }
                }
            }
        }
        stage('Set Next Build Version For Dev Testing') {
            when {
                expression { params.DEV_OR_PUBLISH == "dev" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} init:get-current-version init:get-commit-hash gerrit:get-next-dev-version gerrit:set-unique-version gerrit:set-dev-docker-url"
                    }
                }
            }
        }
        stage('Set Next Build Version For image release') {
            when {
                expression { params.DEV_OR_PUBLISH == "publish" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} init:get-current-version init:get-commit-hash gerrit:get-next-release-version gerrit:set-release-docker-url"
                    }
                }
            }
        }
        stage('Update review with new prefix version') {
            environment {
                GERRIT_REFSPEC = "${env.NEXT_GERRIT_REFSPEC}"
            }
            when {
                expression { params.DEV_OR_PUBLISH == "publish" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} gerrit:clone-repo-restricted gerrit:checkout-patch init:step-version-prefix gerrit:push-review"
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                        sh "${bob} image:ci-helm image:docker-build"
                    }
                }
            }
        }
        stage('Push Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'), file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                        sh "${bob} push:image-push init:write-to-properties-new-version init:write-to-properties-image-path"
                    }
                }
            }
        }
        stage('Submit Review') {
            when {
                expression { params.DEV_OR_PUBLISH == "publish" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "${bob} gerrit:review-change gerrit:submit-change"
                    }
                }
            }
        }
        stage('Archive Artifact Properties') {
            steps {
                script {
                    archiveArtifacts 'artifact.properties'
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

def step_patch_set(number) {
    int current_number = number.toInteger()
    int next_version = current_number + 1;
    return next_version
}

def step_gerrit_refspec_patch_number(refspec) {
    int patchset = refspec.tokenize('/')[-1].toInteger()
    int next_ps = patchset + 1;
    String new_rs = refspec.substring(0,refspec.lastIndexOf('/')) + "/" + next_ps
}