# Upload document on IDP platform using mkdocs.yaml file

[TOC]

## Introduction

This file can be used within a spinnaker flow to create a new document within the cluster according to the input parameters below.

## Overview

Currently, when this file executes, it will:

- Takes in the input parameters discussed in detail below.

-This job will verify successful connection to MINIO storage.

-Generate techdocs from specified files

-Publish generated techdocs to MINIO bucket

## Repo Files
- ci/jenkins/files/createTechDocs.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                      |
| GERRIT_USER_SECRET       | Jenkins secret ID with Gerrit username and password                                                                                                                                                                                                            |                                          |
| GERRIT_BRANCH            | Branch for the change to be pushed.                                                                                                                                                                                                                            | master                                   |
| GERRIT_PROJECT           | Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base                                                                                                                                                                                               |                                          |
| AWS_REGION               | Specify AWS region                                                                                                                                                                                                                                             | eu-west-1                                |
| TECHDOCS_BUCKET_NAME     | The name of the BUCKET where docs are stored                                                                                                                                                                                                                   | techdocs                                 |
| ENTITY_NAME              | Needs to match with catalog-info:metadata:name from the GERRIT_PROJECT                                                                                                                                                                                         |                                          |
| ENTITY_NAMESPACE         | Namespace on cluster                                                                                                                                                                                                                                           | default                                  |
| ENTITY_KIND              | Should be set to the same value as kind property in the catalog-info.yaml eg.component or system                                                                                                                                                               |                                          |
| MINIO_ENDPOINT           | Endpoint to use to connect to a minIO bucket                                                                                                                                                                                                                   | http://osmn.kroto020.rnd.gic.ericsson.se |
| ARMDOCKER_USER_SECRET    | Jenkins secret to log onto the Docker Arm.                                                                                                                                                                                                                     |                                          |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                        |

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
    * **Script Path:** ci/jenkins/files/createTechDocs.Jenkinsfile
> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though.

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