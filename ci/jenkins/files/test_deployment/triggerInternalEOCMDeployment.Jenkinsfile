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
                defaultValue: 'Test-CI-Deployment-From-Product-Review-EO-CM',
                description: 'Webhook for the Spinnaker pipeline to trigger.')
        string(name: 'CHART_NAME',
                defaultValue: 'eric-eo-cm-helmfile',
                description: 'Name of the helmfile to deploy e.g. eric-eo-helmfile')
        string(name: 'CHART_VERSION',
                defaultValue: 'None',
                description: 'Version of the helmfile to deploy')
        string(name: 'CHART_REPO',
                defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm/',
                description: 'Repo of the helmfile to deploy')
        string(name: 'GERRIT_REFSPEC',
                defaultValue: 'None',
                description: 'Gerrit REF Spec is used by Inca to pull down a code review to build a new EO Helmfile to deploy. Takes precedence over CHART_NAME, CHART_VERSION and CHART_REPO')
        string(name: 'GERRIT_BRANCH',
                defaultValue: 'master',
                description: 'Gerrit Branch is used by Inca to pull down a code review to build a new EO Helmfile')
        string(name: 'TAGS',
                defaultValue: 'eoCm',
                description: 'Applications that should be switch on during deployment')
        string(name: 'PATH_TO_SITE_VALUES_FILE',
                defaultValue: 'site-values/eo/ci/template/site-values-latest.yaml',
                description: 'The Path where all the necessary site values are located for the install/upgrade')
        string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
                defaultValue: 'None',
                description: 'The override file path')
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
                defaultValue: 'evo_docker_engine_gic',
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
