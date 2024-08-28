# OSS Check Csars Jenkins File

[TOC]

## Introduction

This script is used to check if the Csars within a specified Helmfile exist within the Czar Repo (Whether the files are AVAILABLE or Not Found).

## Overview

Currently, when the file is executed it will:

- Takes in the input parameters that are discussed below.


- Fetches the .tgz file of the Helmfile specified based off the INT_CHART_REPO, INT_CHART_NAME and INT_CHART_VERSION entered by the user.


- Once this has been completed, we un-tar the Helmfile we have fetched and copy the result into the work directory, we then fetch the site values file from the file path provided (FULL_PATH_TO_SITE_VALUES_FILE) with the specific chart version given (INT_CHART_VERSION).


- By default, if USE_TAGS is false, the get_app_version_from_helmfile.sh will return all the chart name and chart version of all the applications within the helmfile (By performing a Helmfile List). If USE_TAGS is true, it will only showcase the chart names and chart versions that will be installed specified through the tags (By performing a Helmfile List).


- A python3 Docker container will be built with will contain the files that exists within ci/scripts and will contain a folder (output-files) that will contain the artifact.properties outputted when this file is executed.


- The check_for_exisiting_csars.py file is executed which will check to see if the artifact names found through the helmfile list (Or which are contained within the helmfile.tgz) is found within the Csar Repo. If they are found, the artifacts.properties will show AVAILABLE, otherwise it will show NOT FOUND.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkCsars.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/scripts/get_app_version_from_helmfile.sh
- ci/jenkins/scripts/python-ci-scripts/src/check_for_existing_csars.py
- ci/jenkins/scripts/python-ci-scripts/src/csar_executor.py
- ci/jenkins/scripts/python-ci-scripts/src/helmfile_executor.py
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-CSAR-Check/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                     | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_VERSION             | The version of base platform to install.                                                                                                                                                                                                                       |                                                                          |
| ARMDOCKER_USER_SECRET         | Jenkins Secret ID that stores the ARM Docker Credentials.                                                                                                                                                                                                      |                                                                          |
| INT_CHART_NAME                | Integration Chart Name.                                                                                                                                                                                                                                        | eric-eiae-helmfile                                                       |
| INT_CHART_REPO                | Integration Chart Repo.                                                                                                                                                                                                                                        | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| FUNCTIONAL_USER_SECRET        | Jenkins secret ID for ARM Registry Credentials.                                                                                                                                                                                                                | ciloopman-user-creds                                                      |
| FULL_PATH_TO_SITE_VALUES_FILE | Full path within the Repo to the site_values.yaml file.                                                                                                                                                                                                        | site-values/csar-check/site-values.yaml                                  |
| TIMEOUT                       | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT        | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT      | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL                   | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE               | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC                | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

This file holds the details of the Csars (Chart Name and Chart version) and if they are AVAILABLE on the Czar Repo or Not Found.

Example:
```
# File that specifies the Checked Csars.

eric-tm-ingress-controller-cr-crd__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-tm-ingress-controller-cr-crd/6.0.0+37
eric-mesh-controller-crd__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-mesh-controller-crd/5.0.0+114
eric-cloud-native-base__AVAILABLE=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-cloud-native-base/27.0.0
eric-cncs-oss-config__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-cncs-oss-config/0.0.0-3
eric-service-mesh-integration__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-service-mesh-integration/0.0.1-15
eric-oss-common-base__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-common-base/0.1.0-263
eric-eo-so__AVAILABLE=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-eo-so/2.11.0-584
eric-oss-pf__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-pf/2.3.0-17
eric-oss-uds__AVAILABLE=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-uds/4.5.0-6
eric-oss-adc__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-adc/0.0.2-137
eric-oss-dmm__AVAILABLE=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-dmm/0.0.0-51
eric-topology-handling__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-topology-handling/0.0.2-23
eric-oss-ericsson-adaptation__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-ericsson-adaptation/0.1.0-285
eric-oss-app-mgr__NOT_FOUND=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-app-mgr/1.1.0-99
eric-oss-config-handling__AVAILABLE=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/eric-oss-config-handling/0.0.0-38
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
    * **Script Path:** ci/jenkins/files/checkCsars.Jenkinsfile
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
