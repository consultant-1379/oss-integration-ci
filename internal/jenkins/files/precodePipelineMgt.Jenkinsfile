#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review \${GIT_COMMIT}"
def verifications = [
        'Verified'      : -1,
]
def filesChangedInCommit(path) {
    return sh(returnStdout: true, script: "git diff-tree --diff-filter=ACM --no-commit-id --name-only -r $GIT_COMMIT -- $path").trim()
}

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Label of the Jenkins slave where this jenkins job should be executed.')
    }
    stages {
        stage('Clean Workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
                sh "${bob} git-clean"
            }
        }
        stage('Spin Mgt Scripts Linting/Unit Tests') {
            when {
                expression {
                    filesChangedInCommit("internal/pipeline-mgt-scripts/*") != ""
                }
            }
            steps {
                sh "${bob} run-pipeline-mgt-linting-unit-tests"
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
                /*
                always {
                    script {
                        junit 'test_results/*.xml'
                        //tests failed which sets result to unstable ... we want this to be failure.
                        if(currentBuild.result == "UNSTABLE") {
                            currentBuild.result = "FAILURE"
                        }
                    }
                    archiveArtifacts artifacts: 'test_results/**', allowEmptyArchive: true
                }
                */
            }
        }
    }
}
