# Transfer Gerrit Docs to Confluence File

[TOC]

## Introduction

As Ticketmaster have a range of different responsibilities, the team oversees a large amount of documentation.
Some of this documentation resides within Git repositories, meaning its content cannot be searched in Confluence.

This Jenkins job was created so all the Git documentation could be regularly transferred to Confluence, so that its
content can be easily searched.

This job is currently only for use by the Ticketmaster team.

## Overview

Currently, when this file executes, it will:

- Takes in 8 parameters discussed in detail below.


- Searches all the documentation provided in the local repository and creates HTML copies of each file


- If a document is not present in Confluence, it creates a new page for that document on Confluence.


- If a page already exists on Confluence for a document, it will update that page.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/confluence/transferGerritDocsToConfluence.Jenkinsfile *(Main Jenkins File)*

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                   |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| SPACE_KEY                | The Confluence space key of the area where the docs should be uploaded (e.g., DGBase)                                                                                                                                                                          | DGBase                                                                    |
| URL                      | The URL of the Confluence Rest API. This is acquired by appending "/rest/api/content" to the base Confluence URL (e.g., https://confluence-oss.seli.wh.rnd.internal.ericsson.com/rest/api/content)                                                             | https://confluence-oss.seli.wh.rnd.internal.ericsson.com/rest/api/content |
| PARENT_ID                | The Confluence ID of the page where the docs will be uploaded. This can be gotten by viewing "Page Information" in Confluence. The page ID is displayed in the page URL.                                                                                       |                                                                           |
| DOCUMENTS_PATH           | The path to the documents within the oss-integration-ci repo to upload to Confluence (e.g., docs/files)                                                                                                                                                        |                                                                           |
| ARMDOCKER_USER_SECRET    | ARM Docker secret                                                                                                                                                                                                                                              |                                                                           |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                            |                                                                           |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                      |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                        |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                       |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                         |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default  |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                         |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

## Jenkins Job Configuration

> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be done

- Create a new Pipeline Jenkins Job
- Within the "Pipeline" Section of the Jenkins Job Configuration set the following:
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** master
    * **Script Path:** ci/jenkins/files/confluence/transferGerritDocsToConfluence.Jenkinsfile
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
