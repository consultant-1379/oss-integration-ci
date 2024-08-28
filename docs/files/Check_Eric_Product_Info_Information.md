# Check Eric Product Info Information Jenkins File

[TOC]

## Introduction

This script is used to check if the information being added to an eric-product-info.yaml file of an application, is able to correctly pull down the image given the image information (Image Registry, Image Repository Path, Image Name & Image Tag).

## Overview

Currently, when the file is executed it will:

- Takes in the input parameters that are discussed below.

- Runs a docker pull command on the image given the parameters entered within the job.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkEricProductInfoInformation.Jenkinsfile *(Main Jenkins File)*

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                   |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|
| IMAGE_REGISTRY           | Registry for the image to be used.                                                                                                                                                                                                                             | armdocker.rnd.ericsson.se |
| IMAGE_REPO_PATH          | Repository Path for the image to be used.                                                                                                                                                                                                                      | proj-orchestration-so     |
| IMAGE_NAME               | Name of the image to be used.                                                                                                                                                                                                                                  | keycloak-client           |
| IMAGE_TAG                | Tag/Version of the image to be used.                                                                                                                                                                                                                           | 1.0.0-65                  |
| ARMDOCKER_USER_SECRET    | ARM Docker secret                                                                                                                                                                                                                                              |                           |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master         |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                      |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                        |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                       |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine         |

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
    * **Script Path:** ci/jenkins/files/checkEricProductInfoInformation.Jenkinsfile
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
