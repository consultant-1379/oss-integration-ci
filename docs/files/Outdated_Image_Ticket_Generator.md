# Outdated Image Ticket Generator

[TOC]

## Introduction

The Outdated-Image-Ticket-Generator Jenkins job is used to identify shared images across the integration charts and microservices of a specific helmfile version, and create tickets for each integration chart containing outdated images.

## Overview

Currently, when the file is executed, it will

- The Jenkins job build will take input parameters; All parameters have defaults already populated except for the helm file version INT_CHART_VERSION, which is inputted by the user at build time. (All input parameters are listed in more detail below).
- The job then pulls down the helmfile version given. It uses this helmfile to get the application chart versions.
- The job then collects information on all the images contained within the integration charts and their microservices
- Using this image information, a JSON file is created outlining each image, how many versions of that image are used throughout the helmfile, and the location of each image version
- This JSON file is used to determine the latest version of each image
- If the CREATE_TICKETS parameter is set to "True", a ticket will be created for each chart with outdated images. This ticket will be posted onto the Ticketmaster backlog, who will reassign this ticket to the appropriate team
- Two other files are also attached, the outdated_images_per_chart.json file, which only contains the charts with outdated image, and the outdated-ticket-file.txt file, which contains the information to be displayed in the tickets

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/chartImageTicketGenerator.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following job is used internally by Ticketmaster
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Outdated-Chart-Image-Ticket-Generator/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                                                                                                                                                       | Default                                                                    |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| INT_CHART_VERSION        | The version of the helmfile                                                                                                                                                                                                                                                                                                                                                                       |                                                                            |
| INT_CHART_NAME           | Integration Chart Name. Please choose the appropriate repo from the dropdown. <br />IDUN: eric-eiae-helmfile, <br />EO: eric-eo-helmfile <br />EOOM: eric-eoom-helmfile                                                                                                                                                                                                                           | eric-eiae-helmfile                                                         |
| INT_CHART_REPO           | Integration Chart Repo. Please choose the appropriate repo from the dropdown. Note EOs repo has reference to eo in the url. <br />IDUN: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local <br />EO: https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm/ <br />EOOM: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm/eric-eoom-helmfile/ | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local |
| CREATE_TICKETS           | A boolean value to indicate whether tickets should be created or not                                                                                                                                                                                                                                                                                                                              | True                                                                       |
| SKIP_LIST                | An optional comma-separated list of applications to skip when creating tickets (e.g., eric-cloud-native-base,eric-oss-adc)                                                                                                                                                                                                                                                                        | None                                                                       |
| MICROSERVICE_SKIP_LIST   | An optional comma-separated list of microservices to skip when creating tickets (e.g., eric-data-document-database-pg)                                                                                                                                                                                                                                                                            | None                                                                       |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID that stores the ARM Registry Credentials                                                                                                                                                                                                                                                                                                                                        | ciloopman-user-creds                                                        |
| ARMDOCKER_USER_SECRET    | Jenkins Secret ID that stores the ARM Docker Credentials                                                                                                                                                                                                                                                                                                                                          | ciloopman-docker-auth-config                                                |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                                                                                             | 3600                                                                       |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                                                                                     | 60                                                                         |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                                                                                   | 300                                                                        |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                                                                                                                                                           | evo_docker_engine                                                          |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                                                                                                                                                       | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default   |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                                                                                                                                    | refs/heads/master                                                          |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

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
  * **Script Path:** ci/jenkins/files/miniCsarBuilder.Jenkinsfile
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
