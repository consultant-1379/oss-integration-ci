# Get the CRDs from a given chart.

[TOC]

## Introduction

The job is used to gather the crd tar file information from a given application chart. It returns a new properties file with the CHART_NAME, CHART_VERSION and CHART_REPO reset.
This allows all to be delivered at once using ADPs Integration Helm Chart Automation (INCA) enabler.



## Overview
Currently, when the file is executed,
- The Jenkins job will take in parameters from the user (All Input Parameters are listed in more detail below).
- It will pull down the Helmfile and extract all the repo details. This is used during a check, to ensure we have the crd already within the project helmfile.
- It will pull down the application chart and search for the CRDs
- A properties file is generated at the end, with the CHART_NAME, CHART_VERSION and CHART_REPO reset. The file is created whether it find CRDs or not.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkForCrds.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml
- ci/jenkins/scripts/src/crd_executor.py
- ci/jenkins/scripts/src/helmfile_executor.py
- ci/jenkins/scripts/src/utils_executor.py

### Resources

The following is an example of the Jenkinsfile used in a job within the spinnaker flows.
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Check-For-CRDS/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| CHART_NAME               | Application Chart Name to download                                                                                                                                                                                                                             |                                                                          |
| CHART_VERSION            | The version of Application Chart to download and extract                                                                                                                                                                                                       |                                                                          |
| CHART_REPO               | Application Chart Repo to download the helmfile from                                                                                                                                                                                                           |                                                                          |
| HELMFILE_CHART_NAME      | Helmfile Name to download                                                                                                                                                                                                                                      | eric-eiae-helmfile                                                       |
| HELMFILE_CHART_VERSION   | The version of helmfile to download and extract. Use 0.0.0 to get the latest version                                                                                                                                                                           | 0.0.0                                                                    |
| HELMFILE_CHART_REPO      | Helmfile Repo to download the helmfile from                                                                                                                                                                                                                    | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                 | ciloopman-user-creds                                                      |
| FUNCTIONAL_USER_TOKEN    | Jenkins identity token credential for ARM Registry access                                                                                                                                                                                                      | NONE                                                                     |
| SPINNAKER_PIPELINE_ID    | ID of the associated Spinnaker pipeline. Used as a placeholder in order to mitigate Jenkins 404 errors.                                                                                                                                                        | 123456                                                                   |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

* crd_details_artifact.properties - New parameters set for CHART_NAME, CHART_VERSION and CHART_REPO

    Example:
    ```
    CHART_NAME=eric-cloud-native-base, eric-sec-certm-crd, eric-tm-ingress-controller-cr-crd, eric-sec-sip-tls-crd, eric-data-key-value-database-rd-crd
    CHART_VERSION=71.1.0, 4.0.0+69, 11.0.0+29, 5.0.0+29, 1.1.0+1
    CHART_REPO=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm
    ```

    **Note:** If no CRDS are found the properties file is still returned but will just list the original, CHART_NAME, CHART_VERSION and CHART_REPO inputted

    Example:
    ```
    CHART_NAME=eric-cloud-native-base
    CHART_VERSION=71.1.0
    CHART_REPO=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/
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
    * **Script Path:** ci/jenkins/files/checkForCrds.Jenkinsfile
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
