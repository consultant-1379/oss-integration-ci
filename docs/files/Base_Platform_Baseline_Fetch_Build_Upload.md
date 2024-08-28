# OSS Integration Base Platform Baseline Fetch, build & upload helmfile Jenkins file

>> **Note:**
> This is only to be used for the generation of the Base Platform Baseline storage.
> Please contact Ticketmaster for support.


[TOC]

## Introduction

This file is used to generate a helmfile which can be used to store the Base Platform Baseline.
It can be used to generate either a snapshot of the artifact or a released version of the artifact.

## Overview

Currently, when the file is executed it will:

- Clean down the Jenkins workspace before starting a new test flow.
- Set the next version to build for the helmfile
- Updates the version(s) in the helmfile.yaml and crd-helmfile.yaml if appropriate
- Packages up the new helmfile
- Uploads the new helmfile to appropriate repo depending on the GERRIT_PREPARE_OR_PUBLISH option set.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/helmfile/basePlatformBaselineManagement.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                       | Description                                                                                                                                                                                                                                                     | Default                                                                  |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| CHART_NAME                      | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg'. Used to find the specific chart name in the Chart.yaml to swap the correct version for the service.                                                     |                                                                          |
| CHART_VERSION                   | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57. Used to swap out the version according to the CHART_NAME specified in the Chart.yaml.                                                                                             |                                                                          |
| CHART_REPO                      | Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2'.                                                                                         |                                                                          |
| GIT_REPO_URL                    | Gerrit https url to app git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart.                                                                                                                                                          |                                                                          |
| GERRIT_PROJECT                  | Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base                                                                                                                                                                                                |                                                                          |
| GERRIT_BRANCH                   | Branch for the change to be pushed.                                                                                                                                                                                                                             | master                                                                   |
| HELM_INTERNAL_REPO              | Repository to upload the snapshot version to.                                                                                                                                                                                                                   |                                                                          |
| HELM_DROP_REPO                  | Repository to upload the released version to.                                                                                                                                                                                                                   |                                                                          |
| HELMFILE_PATH                   | Relative path to the helmfile in git repo.                                                                                                                                                                                                                      |                                                                          |
| STATE_VALUES_FILE               | Site values file that is used for the helmfile build, this pre-populated file can be found in the oss-integration-ci repo.                                                                                                                                      | None                                                                     |
| VERSION_CHECK_DOWNGRADE         | Default is 'false', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).                                                             | false                                                                    |
| ALLOW_DOWNGRADE                 | Default is 'false', if set to true, downgrade of dependency is allowed.                                                                                                                                                                                         | false                                                                    |
| VERSION_STEP_STRATEGY_MANUAL    | Possible values: MAJOR, MINOR, PATCH. Step the version in metadata.yaml when dependency change received.                                                                                                                                                        | MINOR                                                                    |
| GERRIT_USER_SECRET              | Jenkins secret ID with Gerrit username and password.                                                                                                                                                                                                            |                                                                          |
| GERRIT_PREPARE_OR_PUBLISH       | prepare :: Prepare Helmfile and uploads to the snapshot/internal repo. publish :: Checks in the updates to git and upload to the drop repo                                                                                                                      | prepare                                                                  |
| ARTIFACT_UPLOAD_TO_ARM          | If set to true, will upload the artifact to the specified ARM repository, else it will be attached to the jenkins job as an artifact for local testing. ARTIFACT_UPLOAD_TO_ARM takes presidence over GERRIT_PREPARE_OR_PUBLISH                                  | true                                                                     |
| ARMDOCKER_USER_SECRET           | Jenkins secret to log onto the Docker Arm.                                                                                                                                                                                                                      |                                                                          |
| HELM_REPO_CREDENTIALS_ID        | Repositories.yaml file credential used for auth.                                                                                                                                                                                                                |                                                                          |
| FUNCTIONAL_USER_TOKEN           | Jenkins secret token ID for ARM Registry Token.                                                                                                                                                                                                                 |                                                                          | 
| WAIT_SUBMITTABLE_BEFORE_PUBLISH | For the publish command, wait for the gerrit patch to be set for a verified +1 or +2 or both before submitting, default is true.                                                                                                                                | true                                                                     |
| WAIT_TIMEOUT_SEC_BEFORE_PUBLISH | Timeout in seconds wait for a verifed +1 or +2 or both before submitting. Default is 120s.                                                                                                                                                                      | 120                                                                      |
| TIMEOUT                         | Time to wait in seconds before the job should timeout                                                                                                                                                                                                           | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT          | Number of seconds before the submodule sync command times out                                                                                                                                                                                                   | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT        | Number of seconds before the submodule update command times out                                                                                                                                                                                                 | 300                                                                      |
| AGENT_LABEL                     | Specify the Jenkins agent label that you want the job to run on.                                                                                                                                                                                                | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE                 | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                     | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| CI_REFSPEC                      | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing. | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

On a successful execution an artifact.properties file is created, this artifact lists the details of the created chart.

e.g.

```
INT_CHART_NAME=eric-cicd-base-baseline
INT_CHART_VERSION=0.1.3-1-e97eb2c
INT_CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm
INT_CHART_NAME_STABLE=None
INT_CHART_VERSION_STABLE=None
INT_CHART_REPO_STABLE=None
COMMIT_MESSAGE=[0.1.3] Updated eric-oss-common-base with 0.258.0
COMMIT_REVIEW_URL=https://gerrit-gamma.gic.ericsson.se/#/c/111111111
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
    * **Script Path:** ci/jenkins/files/helmfile/basePlatformBaselineManagement.Jenkinsfile
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
