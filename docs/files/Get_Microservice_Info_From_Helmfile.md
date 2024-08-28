# OSS Gather Microservices information from Helmfile

[TOC]

## Introduction

This file can be used within a spinnaker flow to gather the microservice details present inside the product (EO and EIAP) helmfile.

## Overview

Currently, when the file is executed it will:

- Fetch the helmfile in the .tgz format and extract its contents into the workdir (using the parameters entered).
- Update repository.yaml file i.e. present inside the helmfile directory with repo credentials for those entries where none are provided.
- Download each application chart in the .tgz format from their respective repositories.
- Each of these downloaded TGZ files are then used to obtain microservice information, such as the microservice name, corresponding version and product number, which is stored in the eric-product-info.yaml file of each chart.
- The output is then stored into the Output files created at the end of the job.


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/getMicroserviceInfoFromHelmfile.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml


### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Get-Microservice-Info-From-Helmfile/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                     | Default                                                                  |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_VERSION        | Version(s) of the Chart to build from. Multiple versions can be included, using "," separation only. NOTE: Versions should be in the same order as the Chart Name.                                                                                              |                                                                          |
| INT_CHART_NAME           | Chart Name of Chart(s) to build from. Multiple charts can be included, using "," separation only. NOTE: The first chart name has to be the name of the CSAR.                                                                                                    |                                                                          |
| INT_CHART_REPOS          | Repo(s) to fetch the chart from. Multiple repos can be included, using "," separation only. NOTE: Repos should be in the same order as the Chart Name.                                                                                                          | evo_docker_engine                                                        |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                  | ciloopman-user-creds                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                         | evo_docker_engine                                                        |
| GET_ALL_IMAGES           | Set a true or false boolean to state whether to gather all release info independent of state values file                                                                                                                                                        | true                                                                     |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                     | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                           | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                   | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                 | 300                                                                      |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing. | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

1) helmServicesContent.txt file - This file holds the details of the microservices along with their product number that are contained inside the helmfile in the form of microservices_name:version:product-number.
   e.g. eric-ctrl-bro:6.6.0+15:CXC 201 2182
2) helmfile_services_json_content.json - The file contains the above information in .json format.
3) helmfile_shared_services_json_content.json - This .json file contains the shared microservices as extracted from the above .json file.

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
    * **Script Path:** ci/jenkins/files/getMicroserviceInfoFromHelmfile.Jenkinsfile
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
