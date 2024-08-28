#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review \${GIT_COMMIT}"
def verifications = [
        'Verified'      : -1,
]
def does_commit_contain_file_type(file_extension, path) {
    def commit_sha = sh(returnStdout: true, script: "cd $path && git -C ./ log --pretty=format:'%H' -n 1").trim()
    def files_changed = sh(returnStdout: true, script: "cd $path && git -C ./ show --pretty='format:' --name-only --diff-filter=dr ${commit_sha}").trim()
    for (file in files_changed.split("\n")) {
        if (file.endsWith(file_extension)) {
            return true
        }
    }
    return false
}

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Label of the Jenkins slave where this jenkins job should be executed.')
        string(
            name: 'ARMDOCKER_USER_SECRET',
            defaultValue: 'eoadm100-docker-auth-config',
            description: 'ARM Docker secret'
        )
    }
    stages {
        stage('Clean Workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
                sh "${bob} git-clean"
            }
        }
        stage('Install Docker Config') {
            when {
                anyOf {
                    expression {does_commit_contain_file_type("sh", "ci/jenkins/scripts/")};
                    expression {does_commit_contain_file_type("py", "ci/jenkins/scripts/python-ci-scripts/")}
                }
            }
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                    }
                }
            }
        }
        stage('Shellcheck Scripts') {
            when {
                expression {
                    does_commit_contain_file_type("sh", "ci/jenkins/scripts/")
                }
            }
            steps {
                sh "${bob} shellcheck:run-shellcheck"
            }
        }
        stage('Python-CI Scripts Linting/Unit Tests') {
            when {
                expression {
                    does_commit_contain_file_type("py", "ci/jenkins/scripts/python-ci-scripts/")
                }
            }
            steps {
                sh "${bob} run-python-ci-linting-unit-tests"
            }
            post {
                always {
                    script {
                        junit 'test_results/*.xml'
                        archiveArtifacts artifacts: 'test_results/**', allowEmptyArchive: true
                        //tests failed which sets result to unstable ... we want this to be failure.
                        if (fileExists('test_results/coverage_failed.txt')) {
                            currentBuild.result = "FAILURE"
                        }
                        if(currentBuild.result == "UNSTABLE") {
                            currentBuild.result = "FAILURE"
                        }
                    }
                }
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
    }
}
