# OSS Compare Application Versions From Helmfile Jenkins File

[TOC]

## Introduction

This file can be used within a spinnaker flow to gather the names, versions, repositories and latest versions of the Applications within the Helmfile specified.

## Overview

Currently, when the file is executed it will:


- Take in the input parameters discussed down below.


- The Bob ruleset is executed to run the helmfile_executor.py script, and the compare_application_versions_from_helmfile function.


- The function takes in the STATE_VALUES_FILE and PATH_TO_HELMFILE parameters.


- Two files are archived upon completion.


- The component_name_repo_version.csv file generated contains the name, repo, current version and latest version of the Applications in the Helmfile.


- The component_version_mismatch.txt file generated details the Applications with a version mismatch, i.e., the current version is not the same as the latest version.


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/compareLatestVersionsInHelmfile.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                     | Default                                                                     |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| HELMFILE_CHART_NAME      | The name of the Helmfile to extract                                                                                                                                                                                                                             | eric-eiae-helmfile                                                          |
| HELMFILE_CHART_VERSION   | The version of the Helmfile to extract                                                                                                                                                                                                                          |                                                                             |
| HELMFILE_CHART_REPO      | The repository where the Helmfile is stored                                                                                                                                                                                                                     | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/ |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials.                                                                                                                                                                                                                 | ciloopman-user-creds                                                         |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                        | evo_docker_engine                                                           |
| PATH_TO_HELMFILE         | Path to the helmfile.                                                                                                                                                                                                                                           | eric-eiae-helmfile/helmfile.yaml                                            |
| STATE_VALUES_FILE        | Path to populated site-values file.                                                                                                                                                                                                                             | eric-eiae-helmfile/build-environment/tags_true.yaml                         |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                           | 3600                                                                        |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                   | 60                                                                          |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                 | 300                                                                         |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                     | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default    |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing. | refs/heads/master                                                           |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

The outputted component_name_repo_version.csv file contains the Application names, repositories, current versions in the Helmfile and latest versions from the repositories.
The component_version_mismatch.txt outlines the Applications where the current version does not match the latest version.

Example for component_name_repo_version.csv:
```
Component,Current Version,Latest Version,Repo
eric-tm-ingress-controller-cr-crd,11.1.0+131,11.1.0+132,https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm
```

Example for component_version_mismatch.txt:
```
Version mismatch: eric-tm-ingress-controller-cr-crd
Current version: 11.1.0+131
Latest version: 11.1.0+132
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
    * **Script Path:** ci/jenkins/files/compareLatestVersionsInHelmfile.Jenkinsfile
> **Note:**  * In order to make this pipeline work, the following configuration on Jenkins is required: slave with a specific label (see pipeline.agent.label below)

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
