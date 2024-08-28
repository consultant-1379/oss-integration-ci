# OSS Check Input Parameters Jenkins File

[TOC]

## Introduction

This file is used within the application release spinnaker flows in order to pass in a fixed chart name, chart version, chart repository path.
This file is used to set the appropriate helm chart details depending on the way the flow was executed. There is 2 main ways to use the job.
Firstly, the Check Input Parameters job can be used by other Jenkins jobs were the other jobs will set the parameters of Check Input Parameters job via the other jobs artifact.properties outputs.
Secondly, the Check Input Parameters job can be used in spinnaker flows, where the spinnaker flow will set the parameters of this job via the jobs input parameters (and not based on the output of another jenkins job's output)
The outputs of a job that is run using the checkInputParameters.Jenkinsfile (listed below) are typically used in other parts of the application release spinnaker flows.

## Overview

Currently, when the file is executed it will

- take in a list of the input parameters (listed in more detail below).
- run a bash script that will expose chart details to the rest of the spinnaker flow via the artifact.properties
  based off what input parameters are given to the job.
  The jobs will expose 4 output parameters. CHART_NAME, CHART_VERSION, CHART_REPO and INT_CHART_VERSION. More details on these outputs can be found below
  If the CHART_NAME input parameter is not empty then the CHART_NAME, CHART_VERSION, CHART_REPO and INT_CHART_VERSION input parameters will be exposed in the artifact.properties (please refer to Output File section below for more details)
  Otherwise, If the PARA_CHART_NAME parameter is not empty then the PARA_CHART_NAME, PARA_CHART_VERSION, PARA_CHART_REPO and PARA_INT_CHART_VERSION input parameters will be exposed in the artifact.properties (please refer to Output File section below for more details)
- The job will then expose the artifact.properties file

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkInputParameters.Jenkinsfile *(Main Jenkins File)*

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Check-Parameters/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter              | Description                                                                                                                                                                                                                                                    | Default           |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| CHART_NAME             | Chart Name sent in through a jenkins artifact.properties. This takes precedence over the parmaeter sent to the spinnaker pipeline                                                                                                                              | None              |
| CHART_VERSION          | Chart Version sent in through a jenkins artifact.properties. This takes precedence over the parmaeter sent to the spinnaker pipeline                                                                                                                           | None              |
| CHART_REPO             | Chart REPO sent in through a jenkins artifact.properties. This takes precedence over the parmaeter sent to the spinnaker pipeline                                                                                                                              | None              |
| INT_CHART_VERSION      | Integration Chart Version, sent in through a jenkins artifact.properties. This takes precedence over the parmaeter sent to the spinnaker pipeline                                                                                                              | None              |
| PARA_CHART_NAME        | Chart Name, sent into the pipeline as a parameter by executing the spinnaker pipeline directly.                                                                                                                                                                | None              |
| PARA_CHART_VERSION     | Chart Version, sent into the pipeline as a parameter by executing the spinnaker pipeline directly.                                                                                                                                                             | None              |
| PARA_CHART_REPO        | Chart Repo, sent into the pipeline as a parameter by executing the spinnaker pipeline directly.                                                                                                                                                                | None              |
| PARA_INT_CHART_VERSION | Integration Chart Version, sent into the pipeline as a parameter by executing the spinnaker pipeline directly                                                                                                                                                  | None              |
| SLAVE_LABEL            | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine |
| TIMEOUT                | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600              |
| GERRIT_REFSPEC         | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

The file holds the exposed chart name, version, repository link and the initial chart version, so it can be used in other
parts of the application release spinnaker flow.

Example:
```
CHART_NAME=eric-eo-evnfm
CHART_VERSION=2.23.0-181
CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eo-evnfm-drop-helm
INT_CHART_VERSION=1.36.0-5
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
    * **Script Path:** ci/jenkins/files/checkInputParameters.Jenkinsfile
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
