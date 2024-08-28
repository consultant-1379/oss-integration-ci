#!/usr/bin/env groovy

import groovy.json.JsonOutput

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'SPINNAKER_WEBHOOK',
                defaultValue: 'Test-CI-Deployment-From-Product-Review-EIC',
                description: 'Webhook for the Spinnaker pipeline to trigger.')
        string(name: 'CHART_NAME',
                defaultValue: 'None',
                description: 'Name of the helmfile to deploy e.g. eric-eiae-helmfile')
        string(name: 'CHART_VERSION',
                defaultValue: 'None',
                description: 'Version of the helmfile to deploy')
        string(name: 'CHART_REPO',
                defaultValue: 'None',
                description: 'Repo of the helmfile to deploy')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'None',
                description: 'Gerrit REF Spec is used by Inca to pull down a code review to build a new EIC Helmfile to deploy. Takes precedence over CHART_NAME, CHART_VERSION and CHART_REPO')
        string(name: 'GERRIT_BRANCH',
                defaultValue: 'master',
                description: 'Gerrit Branch is used by Inca to pull down a code review to build a new EIC Helmfile')
        string(name: 'TAGS',
                defaultValue: '',
                description: 'Applications that should be switch on during deployment')
        string(name: 'PATH_TO_SITE_VALUES_FILE',
                defaultValue: 'site-values/idun/ci/template/site-values-latest.yaml',
                description: 'The Path where all the necessary site values are located for the install/upgrade')
        string(name: 'ENV_DETAILS_DIR',
                defaultValue: 'eo-integration-ci/honeypots/pooling/environments',
                description: 'This is the directory within the Repo specified within the Gather-Env-Details Jenkins job where to find the pooling environment details')
        string(name: 'ENV_LABEL',
                defaultValue: 'ticketmaster',
                description: 'This is the label to search for that is attached to the environments in the Lockable Resource Plugin on Jenkins')
        string(name: 'FLOW_URL_TAG',
                defaultValue: 'TicketMaster',
                description: 'Flow URL Tag is used when locking the environment to add a tag to describe what has locked the environment for easier tracking')
        string(name: 'WAIT_TIME',
                defaultValue: '120',
                description: 'This is the time to wait for an Environment to become available. After the time expires the job will fail out')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine_gic_IDUN',
                description: 'Label to choose which Jenkins slave to execute Jenkinsfiles against')
        string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
                description: 'Functional user for logging into armdocker')
        string(name: 'TIMEOUT',
                defaultValue: '3600',
                description: 'Time to wait in seconds before the job should timeout')
        string(name: 'HELM_TIMEOUT',
                defaultValue: '3600',
                description: 'Timeout for helmfile deploy')
        string(name: 'WAIT_SUBMITTABLE_BEFORE_PUBLISH',
                defaultValue: 'true',
                description: 'Executes a check against the review to ensure the review is submittable i.e. has a +1 verified and +2 Code Review. Options true or false')
        string(name: 'CI_GERRIT_REFSPEC',
                defaultValue: 'refs/heads/master',
                description: 'This is the refspec for the jenkins files under tests')
        string(name: 'CI_DOCKER_IMAGE',
                defaultValue: 'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
                description: 'The CI Docker image to be used')
        string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
                defaultValue: 'None',
                description: 'The override file path')
        string(name: 'ALWAYS_RELEASE',
                defaultValue: 'false',
                description: 'Default is \'false\', if set to true, Always upload to released repo with released version, AUTOMATIC_RELEASE is ignored if this is set to true.')
        string(name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'ciloopman-docker-auth-config',
                description: 'ARM Docker secret.')
        string(name: 'CHART_PATH',
                defaultValue: 'helmfile',
                description: 'Relative path to chart.yaml or the helmfile.yaml in git repo.')
        string(name: 'GERRIT_USER_SECRET',
                defaultValue: 'ciloopman-user-creds',
                description: 'Jenkins secret ID with Gerrit username and password.')
        string(name: 'GIT_REPO_URL',
                defaultValue: 'https://gerrit-gamma.gic.ericsson.se/a/OSS/com.ericsson.oss.eiae/eiae-helmfile.git',
                description: 'Gerrit https url to helmfile git repo. Example: https://gerrit-gamma.gic.ericsson.se/a/OSS/com.ericsson.oss.eiae/eiae-helmfile.git.')
        string(name: 'HELM_REPO_CREDENTIALS_ID',
                defaultValue: 'ciloopman_helm_repository_creds',
                description: 'Repositories.yaml file credential used for auth.')
        string(name: 'HELM_DROP_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
                description: 'Drop Helm chart repository url.')
        string(name: 'HELM_INTERNAL_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm',
                description: 'Internal Helm chart repository url.')
        string(name: 'CLEANUP_TYPE',
                defaultValue: 'FULL',
                description: 'Selecting FULL will cleanup deployment helm releases, TLS secrets, Network Policies, Installed PVCs, Deployment namespace, CRD helm releases, CRD components and CRD namespace. Selecting PARTIAL will only cleanup deployment helm releases, TLS secrets, Network Policies, Installed PVCs and Deployment Namespace.')
        string(name: 'NAMESPACE',
                defaultValue: 'oss-deploy',
                description: 'Namespace to be used during the deployment')
        string(name: 'CRD_NAMESPACE',
                defaultValue: 'eric-crd-ns',
                description: 'CRD namespace to be used during the deployment')
        string(name: 'FUNCTIONAL_USER_TOKEN',
                defaultValue: 'NONE',
                description: 'ID for Jenkins identity token for ARM Registry access stored as a credential')
        string(name: 'USE_CERTM',
                defaultValue: 'true',
                description: 'Set to true to use the "--use-certm" tag during the deployment')
        string(name: 'USE_DM_PREPARE',
                defaultValue: 'true',
                description: 'Set to true to use the Deployment Manager function "prepare" to generate the site values file')
    }
    stages {
        stage('Call Spinnaker Webhook') {
            steps {
                script {
                    if (params.GERRIT_HOST != '' && params.GERRIT_PORT != '' && params.GERRIT_SCHEME != '' && params.GERRIT_VERSION != '' && params.SPINNAKER_WEBHOOK != '') {
                        // Empty map that will be a clone of params
                        def paramsCopy = [:]

                        // Populate the copied map with the content of params
                        paramsCopy.putAll(params)

                        // Remove the SPINNAKER_WEBHOOK param, in case it gets used by a job in the flow
                        paramsCopy.remove("SPINNAKER_WEBHOOK")

                        def jsonParams = JsonOutput.toJson(paramsCopy)
                        def payload = '{"parameters": ' + jsonParams + '}'
                        def post = new URL("https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/" + params.SPINNAKER_WEBHOOK).openConnection()
                        post.setRequestMethod("POST")
                        post.setDoOutput(true)
                        post.setRequestProperty("Content-Type", "application/json")
                        post.getOutputStream().write(payload.getBytes("UTF-8"))
                        def postRC = post.getResponseCode()
                        if(postRC.equals(200)) {
                            println(post.getInputStream().getText())
                            println("Started execution: https://spinnaker.rnd.gic.ericsson.se/#/projects/ticketmaster-e2e-cicd/applications/common-cicd/executions?pipeline=" + params.SPINNAKER_WEBHOOK)
                        }
                        else {
                            println(postRC)
                        }
                    }
                }
            }
        }
    }
}