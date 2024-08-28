# getCsarProperties

[TOC]

## Introduction

The getCsarProperties job is used to generate an artifact.properties file with application names and corresponding versions related to the version of helmfile inputted by user. This file is used by the OSS-CSAR-Builder Jenkins job to build the CSARs for the different components, base platform and OSS Applications.


## Overview
Currently, when the file is executed,
- The Jenkins job build will take input parameters by the user (All Input Parameters are listed in more detail below).
- All parameters have default values pre-populated apart from INT_CHART_VERSION which is the version of helmfile inputted by the user.
- This script will fetch the Helmfile within the INT_CHART_REPO for the Helmfile of the same version of the parameter entered (INT_CHART_NAME/INT_CHART_VERSION).
- Once the Helmfile has been fetched, the Helmfile will be extracted and copied to the current work directory.
- The script get_app_version_from_helmfile.sh is called, which will perform a Helm List on the Helmfile fetched previously and add each application name and version to the artifacts.properties file.
- The artifact.properties file is copied to a file called csar.properties where the Artifactory location is inserted between the application name and corresponding versions and appended back into the artifact.properties file.
- The artifact.properties file is attached as an artefact and stored on the Jenkins build and also upload to [Artifactory](https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/)

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/csarProperties.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/scripts/get_app_version_from_helmfile.sh *(Used to get application name and version from the helmfile)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows.
- [Jenkins Jobs](https://fem7s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/getCsarProperties/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_VERSION        | The version of helmfile                                                                                                                                                                                                                                        |                                                                          |
| INT_CHART_NAME           | Helmfile Name                                                                                                                                                                                                                                                  | eric-eiae-helmfile                                                       |
| INT_CHART_REPO           | Helmfile Repo                                                                                                                                                                                                                                                  | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                 | ciloopman-user-creds                                                      |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                        |
| PATH_TO_HELMFILE         | Path to the helmfile                                                                                                                                                                                                                                           | eric-eiae-helmfile/helmfile.yaml                                         |
| STATE_VALUES_FILE        | Path to populated site-values file                                                                                                                                                                                                                             | eric-eiae-helmfile/build-environment/tags_true.yaml                      |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

This artifact.properties file will contain the application name, version and Artifactory location based off the inputs of the job when it runs.

Example:
```
CSAR Built from HELM FILE DETAILS
Helmfile: eric-eiae-helmfile
Helmfile Version: 2.0.0-529
Helmfile Repo: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm

CSARS
eric-tm-ingress-controller-cr-crd=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-tm-ingress-controller-cr-crd/6.0.0+37
eric-mesh-controller-crd=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-mesh-controller-crd/5.0.0+114
eric-cloud-native-base=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-cloud-native-base/27.0.0
eric-cncs-oss-config=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-cncs-oss-config/0.0.0-7
eric-service-mesh-integration=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-service-mesh-integration/0.0.1-16
eric-oss-common-base=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-common-base/0.1.0-266
eric-eo-so=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-eo-so/2.11.0-584
eric-oss-pf=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-pf/2.3.0-20
eric-oss-uds=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-uds/4.6.0-7
eric-oss-adc=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-adc/0.0.2-139
eric-oss-dmm=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-dmm/0.0.0-51
eric-topology-handling=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-topology-handling/0.0.2-23
eric-oss-ericsson-adaptation=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-ericsson-adaptation/0.1.0-295
eric-oss-app-mgr=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-app-mgr/1.1.0-105
eric-oss-config-handling=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-config-handling/0.0.0-38
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
    * **Script Path:** ci/jenkins/files/csarProperties.Jenkinsfile
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
