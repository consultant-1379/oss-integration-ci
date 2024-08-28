#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def bobCommon = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/common/ruleset_kubernetes_range_checks.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Label of the Jenkins slave where this jenkins job should be executed.')
        string(name: 'GERRIT_USER_SECRET', defaultValue: 'eoadm100-user-credentials', description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'GERRIT_REFSPEC', description: 'Ref Spec from the Gerrit review. Example: refs/changes/10/5002010/1.')
    }
    stages {
        stage('Clean Workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
                sh "${bob} git-clean"
            }
        }
        stage('Checkout Commit/Branch') {
            steps {
                script {
                    if (params.GERRIT_REFSPEC) {
                        checkout([$class: 'GitSCM',
                                  branches: [[name: "FETCH_HEAD"]],
                                  doGenerateSubmoduleConfigurations: false,
                                  extensions: [[$class: 'CleanBeforeCheckout']],
                                  submoduleCfg: [],
                                  userRemoteConfigs:  [[credentialsId: params.GERRIT_USER_SECRET, refspec: params.GERRIT_REFSPEC, url: env.GIT_URL]]
                        ])
                    } else {
                        checkout([$class: 'GitSCM',
                                  branches: [[name: params.VCS_BRANCH]],
                                  doGenerateSubmoduleConfigurations: false,
                                  extensions: [[$class: 'CleanBeforeCheckout']],
                                  submoduleCfg: [],
                                  userRemoteConfigs: [[credentialsId: params.GERRIT_USER_SECRET, url: env.GIT_URL]]
                        ])
                    }
                }
            }
        }
        stage('Run kubeconform tests') {
            steps {
                sh "${bobCommon} run-kubernetes-cr-conformance-tests"
            }
        }
    }
}
