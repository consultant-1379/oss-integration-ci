# Reserve Environment Jenkins File

[TOC]

## Introduction

There is several testing pipelines and flows that will need to reserve and un-reserve environments in order to run their flow.

While an environment is reserved, other flows will wait for an environment to become available before continuing. This stops spinnaker flows
and jenkins jobs from conflicting with each other.

The purpose of this file is to provide a jenkins job that can reserve an environment that is needed.

## Overview

Currently, when this file executes, it will:

- Takes in 5 parameters discussed in detail below.


- Uses the jenkins plugin, Lockable Resources, it checks for all resources that are not reserved and contains the ENV_LABEL parameter as a label.


- If resources are not found during WAIT_TIME, it will wait for 30 seconds and will check again to see if a resource is free. If WAIT_TIME is exceeded, the job will fail as no resources were available.


- Once it finds a resource free, it will reserve and lock the resource for the given FLOW_URL.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/reserveResource.Jenkinsfile *(Main Jenkins File)*

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter      | Description                                                                                                                                                                                                                                                    | Default                                                                         |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| ENV_NAME       | Name of the Environment Label to search against                                                                                                                                                                                                                | None                                                                            |
| FLOW_URL_TAG   | Name for the Flow to be used for the URL to append to the Jenkins Job                                                                                                                                                                                          | Spinnaker                                                                       |
| FLOW_URL       | Pipeline URL                                                                                                                                                                                                                                                   | https://spinnaker.rnd.gic.ericsson.se/#/applications/oss-common-base/executions |
| WAIT_TIME      | Time in minutes to wait for resource to become free                                                                                                                                                                                                            | 60                                                                              |
| SLAVE_LABEL    | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                               |
| GERRIT_REFSPEC | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                               |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

There is an artifact.properties file outputted that contains the Name of the Resource that was reserved via the execution of the program.

This artifact.properties file can be used by the Spinakker flow in future jobs.

```
# File that specifies the Resource details.

RESOURCE_NAME=HALL047_BASE_DEPLOY
```

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
    * **Script Path:** ci/jenkins/files/reserveResource.Jenkinsfile
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
