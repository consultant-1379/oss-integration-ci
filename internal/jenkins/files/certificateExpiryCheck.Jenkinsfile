#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets specified in parameters
 */

import java.time.*

def now = new Date()

def bob = "bob/bob -r \${WORKSPACE}/internal/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    parameters {
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
                description: 'Jenkins secret ID with Gerrit username and password')
        string(name: 'JENKINS_API_SECRET',
                defaultValue: 'ossapps100_fem8s11_api_username_and_token',
                description: 'Jenkins secret ID with API username and token')
        string(name: 'GERRIT_REFSPEC',
                description: 'Ref spec of the review under test')
        /*
        string(name: 'GERRIT_REPOS',
                defaultValue: 'OSS/com.ericsson.oss.orchestration.eo/eo-integration-ci',
                description: 'CSV of repos to check')
        */
        string(name: 'EXPIRY_DAYS',
                defaultValue: '10',
                description: 'Number of days to warn on expiry')
        string(name: 'PATH_FILTERS',
                defaultValue: 'app-staging',
                description: 'CSV of path filters for certificate files. Set to "all" to include all paths')
        string(name: 'EXCLUDES',
                defaultValue: '',
                description: 'CSV of keywords for excluding paths')
        string(name: 'SUBMODULE_SYNC_TIMEOUT',
                defaultValue: '60',
                description: 'The amount of time to wait in seconds for all the submodules to clone when executing the \"gerrit clone\" command')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'PIPELINE_MGT_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-dev/eric-oss-pipeline-mgt-scripts:latest',
                description: 'Pipeline-mgt CI image to use (set to "local" to build inline)')
        string(name: 'DISTRIBUTION_EMAIL',
                defaultValue: 'PDLAPPSTAG@pdl.internal.ericsson.com',
                description: 'Email address to send expiry status report for certificates.')
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
        stage('Run Certificate Expiry Checks') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: params.GERRIT_USER_SECRET, usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD'),
                                     usernamePassword(credentialsId: params.JENKINS_API_SECRET, usernameVariable: 'JENKINS_USER', passwordVariable: 'JENKINS_TOKEN')]) {
                        /*
                        script {
                            String[] str;
                            repos = params.GERRIT_REPOS.split(',');
                            for( String repo : repos ) {
                                path_elems = repo.split('/');
                                env.FULL_REPO_NAME = repo;
                                env.REPO_NAME = path_elems.last();
                                sh "${bob} run-cert-expiry-repo-checks"
                            }
                        }
                        */
                        sh "${bob} run-cert-expiry-repo-checks"
                        eoIntegrationReportHTML = readFile "report_eo-integration-ci.html"
                        ossIntegrationReportHTML = readFile "report_oss-integration-ci.html"
                        ossCommonCIReportHTML = readFile "report_oss-common-ci.html"
                        emailBody = eoIntegrationReportHTML + "<br/>"
                        emailBody += ossIntegrationReportHTML + "<br/>"
                        emailBody += ossCommonCIReportHTML
                    }
                }
            }
        }
        stage('Archive Summary Reports') {
            steps {
                script {
                    archiveArtifacts 'report_eo-integration-ci.html'
                    archiveArtifacts 'report_oss-integration-ci.html'
                    archiveArtifacts 'report_oss-common-ci.html'
                }
            }
        }
    }
    post {
        success {
            script {
                // Send out summaries
                emailext subject: "JFYI :: App-Staging Repo Certificate Expiry Summary Report ${now.format('dd.MM.yy (HH:mm)', TimeZone.getTimeZone('UTC'))}",
                            from: 'NoReply@ericsson.com',
                            to: "${params.DISTRIBUTION_EMAIL}",
                            mimeType: 'text/html',
                            body: emailBody
            }
        }
        always {
            cleanWs()
        }
    }
}
