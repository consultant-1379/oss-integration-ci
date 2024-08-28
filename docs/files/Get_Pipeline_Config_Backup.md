# OSS Get Pipeline Config Backup Jenkins File

[TOC]

## Introduction

This file will obtain the config files of Pipelines within a Spinnaker Project and push the config files to the oss-integration-ci repository.

The result of this script will be a success/failure email notification to the email specified in the DISTRIBUTION_EMAIL parameter as described in the Input Parameters below.

## Overview

Currently, when the file is executed it will:

- Takes in 6 parameters discussed in the input parameters below.


- Loop through each pipeline name within a Spinnaker Project and will return a JSON String result of each Pipeline containing the location of the Pipeline config file.


- Once this has been completed, the config files are pushed to the oss-integration-ci repository.


- If the scripts were successful, there will be a successful notification sent to the DISTRIBUTION_EMAIL.


- If the script has failed, there will be a failure notification sent to the DISTRIBUTION_EMAIL.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/getPipelineConfigBackup.Jenkinsfile *(Main Jenkins File)*

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Backup-Pipelines-ossapp/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter             | Description                                                                                                                                                                                                                                                    | Default                                                                                                    |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| SPINNAKER_SVC_CRED_ID | Jenkins secret ID for ARM Registry Credentials.                                                                                                                                                                                                                | eoadm100-user-credentials                                                                                  |
| NODE_LABEL            | Nodes having this label can execute this pipeline.                                                                                                                                                                                                             | evo_docker_engine                                                                                          |
| DISTRIBUTION_EMAIL    | Email address to send notification status of the Jenkins job.                                                                                                                                                                                                  |                                                                                                            |
| APP_PIPELINES         | List of pipelines for backing up from app pipelines.                                                                                                                                                                                                           | OSS-Common-Base-Submit-Flow                                                                                |
| SPINNAKER_PROJECT     | Name of application within spinnaker to get backup from.                                                                                                                                                                                                       | oss-common-base                                                                                            |
| PIPELINE_URL          | URL of the pipeline used in notification e-mail.                                                                                                                                                                                                               | https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Backup-Pipelines-ossapp/ |
| GERRIT_REFSPEC        | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                                                          |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

No artifact.properties file is outputted from this script.

This script outputs an email to the specified DISTRIBUTION_EMAIL entered, containing the Pipeline URL and regarding whether the script has been a Success or Failure.

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
    * **Script Path:** ci/jenkins/files/getPipelineConfigBackup.Jenkinsfile
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
