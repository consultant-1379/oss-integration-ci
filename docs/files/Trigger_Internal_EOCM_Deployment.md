# Internal EO CM Deployment Pipeline Trigger Jenkins File

[TOC]

## Introduction

This file is used to trigger an internal Spinnaker Pipeline to install an EO CM Helmfile from a review or specific version.

The internal Spinnaker Pipeline that is triggered is [Test-CI-Deployment-From-Product-Review-EO-CM](https://spinnaker.rnd.gic.ericsson.se/#/projects/ticketmaster-e2e-cicd/applications/common-cicd/executions?q=Test-CI&pipeline=Test-CI-Deployment-From-Product-Review-EO-CM)

## Overview

Currently, when the file is executed it will:

- Take in a SPINNAKER_WEBHOOK_PARAMETER from the relevant Jenkins job's configuration


- Convert the parameters in the job (listed below) to JSON for use with a POST request.


- Send a POST request with the JSON body to the following endpoint to trigger the pipeline - https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/(params.SPINNAKER_WEBHOOK)


- Print the 200 response code and the response body if successful, otherwise print the response code.


### Repo Files
The following file(s) within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/test_deployment/triggerInternalEOCMDeployment.Jenkinsfile *(Main Jenkins File)*

### Resources

The following job is used to submit to the pipeline
- [Trigger-Internal-EOCM-Deployment](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/TicketMaster/job/Trigger-Internal-EOCM-Deployment/)

### Parameters

#### Input Parameters

The following Webhook parameter must be configured in the Submit job's configuration, to append the relevant value onto the Webhook URL

| Parameter         | Description                                    | Default Value                                 |
|-------------------|------------------------------------------------|-----------------------------------------------|
| SPINNAKER_WEBHOOK | Webhook for the Spinnaker pipeline to trigger. | Test-CI-Deployment-From-Product-Review-EO-CM  |

The following parameters are passed through to Spinnaker by the Jenkins job.

| Parameter                         | Description                                                                                                                              | Default Value                                                            |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| CHART_NAME                        | Name of the helmfile to deploy e.g. eric-eo-cm-helmfile                                                                                  | eric-eo-cm-helmfile                                                      |
| CHART_VERSION                     | Version of the helmfile to deploy                                                                                                        | None                                                                     |
| CHART_REPO                        | Repo of the helmfile to deploy                                                                                                           | https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm/          |
| GERRIT_REFSPEC                    | Gerrit REF Spec is used by Inca to pull down a code review to build a new EO CM Helmfile                                                 | None                                                                     |
| GERRIT_BRANCH                     | Gerrit Branch is used by Inca to pull down a code review to build a new EO CM Helmfile                                                   | master                                                                   |
| TAGS                              | Applications that should be switch on during deployment                                                                                  | eoCM                                                                     |
| PATH_TO_SITE_VALUES_FILE          | The Path where all the necessary site values are located for the install/upgrade                                                         | site-values/eo/ci/template/site-values-latest.yaml                       |
| ENV_DETAILS_DIR                   | This is the directory within the Repo specified within the Gather-Env-Details Jenkins job where to find the pooling environment details  | eo-integration-ci/honeypots/pooling/environments                         |
| ENV_LABEL                         | This is the label to search for that is attached to the environments in the Lockable Resource Plugin on Jenkins                          | ticketmaster                                                             |
| FLOW_URL_TAG                      | Flow URL Tag is used when locking the environment to add a tag to describe what has locked the environment for easier tracking           | TicketMaster                                                             |
| WAIT_TIME                         | This is the time to wait for an Environment to become available. After the time expires the job will fail out                            | 120                                                                      |
| SLAVE_LABEL                       | Label to choose which Jenkins slave to execute Jenkinsfiles against                                                                      | evo_docker_engine_gic_IDUN                                               |
| FUNCTIONAL_USER_SECRET            | Functional user for logging into armdocker                                                                                               | ciloopman-user-creds                                                     |
| TIMEOUT                           | Time to wait in seconds before the job should timeout                                                                                    | 3600                                                                     |
| HELM_TIMEOUT                      | Timeout for helmfile deploy                                                                                                              | 3600                                                                     |
| WAIT_SUBMITTABLE_BEFORE_PUBLISH   | Executes a check against the review to ensure the review is submittable i.e. has a +1 verified and +2 Code Review. Options true or false | true                                                                     |
| CI_GERRIT_REFSPEC                 | This is the refspec for the jenkins files under tests                                                                                    | refs/heads/master                                                        |
| CI_DOCKER_IMAGE                   | The CI Docker image to be used                                                                                                           | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| PATH_TO_SITE_VALUES_OVERRIDE_FILE | The override file path                                                                                                                   | None                                                                     |

## Jenkins Job Configuration
> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be followed

- Create a new Pipeline Jenkins Job
- Within the "Pipeline Section" of the Jenkins Job Configuration set the following
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** master
    * **Script Path:** ci/jenkins/files/test_deployment/triggerInternalEOCMDeployment.Jenkinsfile
> **Note:** In order for the pipeline to work, the Credentials plugin should be installed and have the following secret: c12a011-config-file (admin.config to access c12a011 cluster)

> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though.

### Testing

In order to test a Jenkins file (Without affecting the master branch), please refer to the [Contributing Guide](../Contribution_Guide.md).

## Contributing

We are an inner source project and welcome contributions. See our
[Contributing Guide](../Contribution_Guide.md) for details.

## Contacts

### Guardians

See in [Contributing Guide](../Contribution_Guide.md)

### Backlog

Create a new issue on Ticketmaster component under IDUN project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
