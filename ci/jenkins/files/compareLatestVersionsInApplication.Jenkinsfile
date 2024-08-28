#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def common_functions

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'HELMFILE_CHART_VERSION', defaultValue: '0.0.0', description: 'The version of the Helmfile sent in through a previous jenkins build\'s artifact.properties.')
        string(name: 'HELMFILE_CHART_REPO', defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/', description: 'The repository in which the Helmfile is stored.')
        string(name: 'HELMFILE_CHART_NAME', defaultValue: 'eric-eiae-helmfile', description: 'The name of the Helmfile to be used')
        string(name: 'CHART_NAME', defaultValue: 'eric-oss-common-base', description: 'Name of the Application Chart to compare the Microservice versions.')
        string(name: 'CHART_REPO', defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local', description: 'The repository in which the Application Chart is stored')
        string(name: 'CHART_VERSION', defaultValue: '0.0.0', description: 'The version of the Chart used to compare its microservice versions')
        string(name: 'TIMEOUT', defaultValue: '3600', description: 'Time to wait in seconds before the job should timeout')
        string(name: 'SUBMODULE_SYNC_TIMEOUT', defaultValue: '60', description: 'Number of seconds before the submodule sync command times out')
        string(name: 'SUBMODULE_UPDATE_TIMEOUT', defaultValue: '300', description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine', description: 'Specify the slave label that you want the job to run on')
        string(name: 'FUNCTIONAL_USER_SECRET', defaultValue: 'ciloopman-user-creds', description: 'Jenkins secret ID for ARM Registry Credentials')
        string(name: 'ARMDOCKER_USER_SECRET', defaultValue: 'ciloopman-docker-auth-config', description: 'ARM Docker secret')
        string(name: 'GERRIT_USER_SECRET', defaultValue: 'eoadm100-user-credentials', description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'CI_DOCKER_IMAGE', defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default', description: 'CI Docker image to use. Mainly used in CI Testing flows')
        string(name: 'GERRIT_REFSPEC', defaultValue: 'refs/heads/master', description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master)')
        string(name: 'PATH_TO_HELMFILE', defaultValue: 'eric-eiae-helmfile/helmfile.yaml', description: 'Path to the helmfile')
        string(name: 'STATE_VALUES_FILE', defaultValue: 'eric-eiae-helmfile/build-environment/tags_true.yaml', description: 'Path to populated site-values file')
    }
    environment {
        CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Prepare') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                script {
                    common_functions = load('ci/jenkins/pipeline/functions/groovy/lib/common.groovy')

                    common_functions.command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                    common_functions.command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                    sh "${bob} git-clean"
                }
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                    }
                }
            }
        }
        stage('Get Helmfile and extract') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh "${bob} helmfile:fetch-helmfile"
                    sh "${bob} helmfile:extract-helmfile"
                }
            }
        }
        stage('Compare Microservice Versions in the Application') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'), usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                    sh "${bob} compare-component-versions:compare-microservice-versions-in-application"
                }
                archiveArtifacts 'component_name_repo_version.csv'
                archiveArtifacts 'component_version_mismatch.txt'
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}

def get_ci_docker_image_url(ci_docker_image) {
    if (ci_docker_image.contains("default")) {
        String latest_ci_version = readFile "VERSION_PREFIX"
        String trimmed_ci_version = latest_ci_version.trim()
        url = ci_docker_image.split(':');
        return url[0] + ":" + trimmed_ci_version;
    }
    return ci_docker_image
}

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}
