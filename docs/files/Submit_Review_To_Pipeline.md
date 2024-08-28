# OSS Product Staging Trigger Jenkins File

[TOC]

## Introduction

This file is used to trigger a Spinnaker Staging Pipeline, when a Submit-To-Pipeline +1 label is provided to the relevant Helmfile/Application change.

## Overview

Currently, when the file is executed it will:

- Take in a SPINNAKER_WEBHOOK_PARAMETER from the relevant Jenkins job's configuration


- Convert the standard Gerrit parameters passed in from the Gerrit review (listed below) to JSON for use with a POST request.


- Send a POST request with the JSON body to the following endpoint to trigger the pipeline - https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/(params.SPINNAKER_WEBHOOK)


- Print the 200 response code and the response body if successful, otherwise print the response code.


### Repo Files
The following file(s) within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/submitReviewToPipeline.Jenkinsfile *(Main Jenkins File)*

### Resources

The following jobs are used to submit reviews to pipelines
- [OSS-IDUN-HelmFile-Submit-Review-To-Pipeline](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/TicketMaster/job/OSS-IDUN-HelmFile-Submit-Review-To-Pipeline/)
- [EO-HelmFile-Submit-Review-To-Pipeline](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/TicketMaster/job/EO-HelmFile-Submit-Review-To-Pipeline/)
- [OSS-Common-Base-Submit-Review-To-Pipeline](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Common-Base-Submit-Review-To-Pipeline/)

### Parameters

#### Input Parameters

The following Webhook parameter must be configured in the Submit job's configuration, to append the relevant value onto the Webhook URL

| Parameter         | Description                                    | Default Value |
|-------------------|------------------------------------------------|---------------|
| SPINNAKER_WEBHOOK | Webhook for the Spinnaker pipeline to trigger. |               |

The following is a list of parameters that are passed in by Gerrit.

| Parameter                      | Description                                                            |
|--------------------------------|------------------------------------------------------------------------|
| GERRIT_EVENT_TYPE              | The type of action taking place on the review, e.g. comment-added.     |
| GERRIT_EVENT_HASH              | A hashcode of the Gerrit event object.                                 |
| GERRIT_CHANGE_WIP_STATE        | Parameter name to change wip state.                                    |
| GERRIT_CHANGE_PRIVATE_STATE    | Parameter name to change private state.                                |
| GERRIT_BRANCH                  | Parameter name for the branch.                                         |
| GERRIT_TOPIC                   | Parameter name for the topic.                                          |
| GERRIT_CHANGE_NUMBER           | Parameter name for the change number.                                  |
| GERRIT_CHANGE_ID               | Parameter name for the change id.                                      |
| GERRIT_PATCHSET_NUMBER         | Parameter name for the patchset number.                                |
| GERRIT_PATCHSET_REVISION       | Parameter name for the patchset revision.                              |
| GERRIT_REFSPEC                 | Parameter name for the refspec.                                        |
| GERRIT_PROJECT                 | Parameter name for the Gerrit project name                             |
| GERRIT_CHANGE_SUBJECT          | Parameter name for the the commit subject (commit message's 1st line). |
| GERRIT_CHANGE_COMMIT_MESSAGE   | Parameter name for the full commit message.                            |
| GERRIT_CHANGE_URL              | Parameter name for the url to the change.                              |
| GERRIT_CHANGE_OWNER            | The name and email of the owner of the change.                         |
| GERRIT_CHANGE_OWNER_NAME       | The name of the owner of the change.                                   |
| GERRIT_CHANGE_OWNER_EMAIL      | The email of the owner of the change.                                  |
| GERRIT_PATCHSET_UPLOADER       | The name and email of the uploader of the patch-set.                   |
| GERRIT_PATCHSET_UPLOADER_NAME  | The name of the uploader of the patch-set.                             |
| GERRIT_PATCHSET_UPLOADER_EMAIL | The email of the uploader of the patch-set.                            |
| GERRIT_EVENT_COMMENT_TEXT      | Comment posted to Gerrit in a comment-added event.                     |
| GERRIT_EVENT_ACCOUNT           | The name and email of the person who triggered the event.              |
| GERRIT_EVENT_ACCOUNT_NAME      | The name of the person who triggered the event.                        |
| GERRIT_EVENT_ACCOUNT_EMAIL     | The email of the person who triggered the event.                       |
| GERRIT_NAME                    | The name of the Gerrit instance.                                       |
| GERRIT_HOST                    | The host of the Gerrit instance.                                       |
| GERRIT_PORT                    | The port number of the Gerrit instance.                                |
| GERRIT_SCHEME                  | The protocol scheme of the Gerrit instance.                            |
| GERRIT_VERSION                 | The version of the Gerrit instance.                                    |

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
    * **Script Path:** ci/jenkins/files/submitReviewToPipeline.Jenkinsfile
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

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
