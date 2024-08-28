# OSS Set Or Get the Base Platform Baseline from the Given Helmfile

>> **Note:**
> Internal Use Only. This file is only to be used to generate a baseline for the base platform applications.

[TOC]

## Introduction

This file can be used within a spinnaker flow to either return the baseline from a given Helmfile or to set a new
baseline by taking the given chart details and swapping those details from the helmfile App details returned.

## Overview

- The Jenkins file takes in a number of parameters these are discussed down below.

- Currently, when the file is executed it will:
  - If "NO" Helm Chart details are given
    - This script will fetch the Helmfile from the specified helmfile repo.
    - Extracts the helmfile.
    - Fetches all the application details from the helmfile using "helmfile list" command.
    - Generates an artifact.properties
  - If Helm Chart details are given
    - This script will fetch the Helmfile from the specified helmfile repo.
    - Extracts the helmfile.
    - Fetches all the application details from the helmfile using "helmfile list" command
    - Iterate over the Helmfile App content and swap the given Chart details from the list to generate new baseline
    details.
    - Generates an artifact.properties

- The artifact.properties file is archived and returned containing the chart names and their corresponding versions.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/helmfile/setGetBasePlatformBaselineAppVersions.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                     | Default                                                                  |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| HELMFILE_NAME            | Helmfile Name e.g. eric-eiae-helmfile                                                                                                                                                                                                                           |                                                                          |
| HELMFILE_VERSION         | helmfile version                                                                                                                                                                                                                                                |                                                                          |
| HELMFILE_REPO            | Helmfile Repo                                                                                                                                                                                                                                                   |                                                                          |                                                                                                                                                                                                                                            |                                                                          |
| CHART_NAME               | Helm Chart Name.                                                                                                                                                                                                                                                |                                                                          |
| CHART_VERSION            | Helm Chart Version.                                                                                                                                                                                                                                             |                                                                          |
| CHART_REPO               | Helm Chart Repo.                                                                                                                                                                                                                                                |                                                                          |
| PROJECT_FILE_NAME        | Used if the project under test has specific base applications that it does not use. See note on "Helmfile Labels" below                                                                                                                                         | None                                                                     |
| PATH_TO_HELMFILE         | Path to the helmfile.                                                                                                                                                                                                                                           |                                                                          |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials.                                                                                                                                                                                                                 |                                                                          |
| ARMDOCKER_USER_SECRET    | Jenkins secret ID for the ARM Docker Credentials                                                                                                                                                                                                                |                                                                          |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                           | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                   | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                 | 300                                                                      |
| AGENT_LABEL              | Specify the Jenkins agent label that you want the job to run on.                                                                                                                                                                                                |                                                                          |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                     | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing. | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

**Note - Helmfile Labels**

Labels in the oss-base-baseline helmfile/crd-helmfile yaml files can be used to distinguish if a certain project should
retrieve the application information.

See below for an example, it shows that eric-data-wide-column-database-cd-crd is
only applicable for the EIAP project, "labels.project.eric-eiae-helmfile". Any other project if set in the
PROJECT_FILE_NAME parameter will not pick up this application information.

If PROJECT_FILE_NAME parameter is left at default then no check will be performed and all base applications will be
picked up.

  ```
  - name: eric-data-wide-column-database-cd-crd
    namespace: {{ .Values | get "helmfile.crd.namespace" "eric-crd-ns" }}
    chart: {{ .Values | get "repository" "adp-gs-all" }}/eric-data-wide-column-database-cd-crd
    labels:
        project: eric-eiae-helmfile
    version: 1.23.0+30
    values:
      - "./values-templates/global-values.yaml.gotmpl"
      - "./values-templates/release-site-values.yaml.gotmpl"
  ```
#### Output File
- Structure of the generated artifact.properties has info in two formats
    - A format INCA can consume.
    ```
    BASE_PLATFORM_BASELINE_CHART_NAME=eric-cloud-native-service-mesh,eric-cnbase-oss-config
    BASE_PLATFORM_BASELINE_CHART_VERSION=9.1.0,1.7.0
    BASE_PLATFORM_BASELINE_CHART_REPO=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm,https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/
    ```
    - Each Application can also be fetched individually
    ```
    eric-oss-common-base_name=eric-oss-common-base
    eric-oss-common-base_version=0.185.0
    eric-oss-common-base_repo=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
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
    * **Script Path:** ci/jenkins/files/helmfile/setGetBasePlatformBaselineAppVersions.Jenkinsfile
> **Note:**  * In order to make this pipeline work, the following configuration on Jenkins is required: agent with a specific label (see pipeline.agent.label below)

> **Note:** In order for the pipeline to work, the Credentials plugin should be installed and have the appropriates secrets in the Jenkins credentials.

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
