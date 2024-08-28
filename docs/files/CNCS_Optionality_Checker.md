# OSS CNCS Optionality Checker

[TOC]

## Introduction

The OSS-CNCS-Optionality-Checker Jenkins job is used to assess whether all the services contained within the CNCS Chart.yaml file are also contained within the optionality.yaml file of the helmfile.

## Overview

Currently, when the file is executed, it will:

- Take in a number of different parameter values, which are described in greater detail below.
- The job then pulls down the baseline helmfile based on the parameters provided and untars the file.
- The job then identifies which version of the common-base and CNCS charts are contained within the helmfile. It then pulls these chart versions and untars them.
- The job then extracts the CNCS optionality values file contained within common-base and the microservice dependencies within the Chart.yaml file of the CNCS chart. These values are then compared and if any values are missing from the optionality.yaml file, an exception is thrown.
- Regardless of whether the job fails, the job artifacts a text file outlining the helmfile name and version and the CNCS name and version. If the job fails, the missing values are added to the text file.
- This artifact is stored on the build for 24hrs, and the Jenkins job will only keep the last 4 builds.

## Repo Files

The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/cncsOptionalityCheck.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_VERSION        | The version of the base baseline helmfile to examine                                                                                                                                                                                                           |                                                                          |
| ARMDOCKER_USER_SECRET    | Jenkins Secret ID that stores the ARM Docker Credentials. These credentials are used to access Docker images as part of the job                                                                                                                                | ciloopman-docker-auth-config                                              |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID that stores the ARM Registry Credentials. These credentials are used to download the base baseline helmfile                                                                                                                                  | ciloopman-user-creds                                                      |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

After a successful build, the artifacts file will outline that name and version of the helmfile and CNCS chart.

It will also outline that all the microservices contained within the CNCS chart are included in the helmfile optionality.yaml file:

```
------------------------------
Helmfile name and version: base-platform-baseline-0.421.0
eric-oss-common-base version: 0.635.0
eric-cloud-native-base version: 179.3.0
------------------------------
All CNCS optionality files are contained in common-base
```

After a failed build, the artifacts file will outline that name and version of the helmfile and CNCS chart.

It will also outline all the CNCS microservice values that are missing from the optionality.yaml file:

```
------------------------------
Helmfile name and version: base-platform-baseline-0.421.0
eric-oss-common-base version: 0.635.0
eric-cloud-native-base version: 179.3.0
------------------------------
CNCS optionality values that are missing from common-base
eric-si-application-sys-info-handler
eric-data-key-value-database-rd
eric-cloud-native-kvdb-rd-operand
eric-lcm-smart-helm-hooks
```

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
  * **Script Path:** ci/jenkins/files/cncsOptionalityCheck.Jenkinsfile
> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though.

## Testing

In order to test a Jenkins file (Without affecting the master branch), please refer to the [Contributing Guide](../Contribution_Guide.md).

## Contributing

We are an inner source project and welcome contributions. See our
[Contributing Guide](../Contribution_Guide.md) for details.

## Contacts

## Guardians

See in [Contributing Guide](../Contribution_Guide.md)

## Backlog

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../Contribution_Guide.md) for further details

## Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
