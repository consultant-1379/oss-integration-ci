# Get Latest Chart or Helmfile Jenkins File

[TOC]

## Introduction

The main purpose of this jenkins file is to create and maintain the Get-Latest-ChartOrHelmfile jenkins jobs.
This job is used as part of multiple spinnaker flows and it is used to fetch the latest version of a given helm chart or helmfile.
It does this by looking at the repository of the given helm chart or helmfile and finding the latest artifact added to the given repository that matches
the name of the helm chart or helmfile that was passed into the job.

## Overview

The jenkins job created from this jenkinsfile will do the following:

1. Pull down the oss-integration-ci repo and use git clean to clean up any untracked files.
2. Using the Functional User provided in the input of the job, the job will do one of two things:
    1. If an INT_CHART_VERSION input parameter is provided, the job will pass this version in the output artifact.properties file
    2. Otherwise, the job will use the bob framework and docker to run python scripts to fetch the latest helm chart or helmfile version using the
       FUNCTIONAL_USER_SECRET, INT_CHART_NAME and INT_CHART_VERSION input parameters.
3. Assuming there were no issues in step 2, the job will create an artifact.properties file that will store a key pair value that contains the
   latest helm chart or helmfile version based on the inputs of the job.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkHelmfileDeployment.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml
- ci/jenkins/scripts/python-ci-scripts

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Get-Latest-ChartOrHelmfile/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| SLAVE_LABEL              | Label of the Jenkins slave where this jenkins job should be executed.                                                                                                                                                                                          | evo_docker_engine                                                        |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password.                                                                                                                                         | ciloopman-user-creds                                                      |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SPINNAKER_PIPELINE_ID    | ID of the associated Spinnaker pipeline. Used as a placeholder in order to mitigate Jenkins 404 errors.                                                                                                                                                        | 123456                                                                   |
| TIMEOUT                  | Time to wait in seconds before the job should timeout.                                                                                                                                                                                                         | 3600                                                                     |
| INT_CHART_NAME           | The name of the Integration Chart or Helmfile to be searched                                                                                                                                                                                                   | eric-eiae-helmfile                                                       |
| INT_CHART_VERSION        | The version of the Integration Chart of Helmfile sent in through a previous jenkins build's artifact.properties.                                                                                                                                               | 0.0.0                                                                    |
| INT_CHART_REPO           | The repository in which the Integration chart or Helmfile will be stored.                                                                                                                                                                                      | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

This artifact.properties file will contain the latest helm chart or helmfile version based off the inputs of the job when it runs.

Example:
```
INT_CHART_VERSION:2.0.0-482
```
## Jenkins Job Configuration

> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be followed

- Create a new Pipeline Jenkins Job
- Within the "Pipline Section" of the Jenkins Job Configuration set the following
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** master
    * **Script Path:** ci/jenkins/files/getLatestChartOrHelmfile.Jenkinsfile
> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though.

### Testing

In order to test a Jenkins file (Without affecting the master branch), please refer to the [Contributing Guide](../Contribution_Guide.md).

## Contributing

We are an inner source project and welcome contributions. See our
[Contributing Guide](../Contribution_Guide.md) for details.

## Contacts

### Guardians

See in [Contributing Guide](./contribution-guide.md)

### Backlog

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
