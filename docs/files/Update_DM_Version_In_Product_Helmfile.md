# OSS Update DM Version in Product Helmfile and push review.

[TOC]

## Introduction

The "update DM Version In Product Helmfile", Jenkins job is used to update the Deployment manager (DM) version in the specified Product Helmfile.
This version is used to map the deployment manager version to the product helm file.

## Overview

Currently, when the file is executed, it will:

- Takes in a number of different parameter values, which are described in greater detail below.
- The job pulls down the specified product helmfile repo.
- Using the version specified for DM, it updates the dm_version.yaml within the helmfile directory, with the new version.
- It generates a new gerrit review with the change and pushes the changes for review.
- If the CODE_REVIEW_ONLY parameter is 'true', it adds a +2 Code Review label to the gerrit review.
- If the CODE_REVIEW_ONLY parameter is 'false', it adds a +2 Code Review and +1 verified label to the gerrit review.
- Generates a file called gerrit_create_patch.properties, with a number of Gerrit review properties that can be used
by subsequent stages in the pipeline

## Repo Files

The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/updateVersionInProductHelmfile.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base flow.
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/updateDMVersionInProductHelmfile/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                       | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| GERRIT_PROJECT                  | Gerrit project details e.g. OSS/com.ericsson.oss.aeonic/oss-integration-ci                                                                                                                                                                                     |                                                                          |
| GERRIT_BRANCH                   | Gerrit branch the review should be submitted to.                                                                                                                                                                                                               | master                                                                   |
| COMMIT_MESSAGE_FORMAT_MANUAL    | Gerrit commit message to attach to the review                                                                                                                                                                                                                  | NO JIRA - Version Prefix updated                                         |
| PREFIX_VERSION                  | New Version to be set in the file                                                                                                                                                                                                                              |                                                                          |
| WAIT_SUBMITTABLE_BEFORE_PUBLISH | Executes a check against the review to ensure the review is submittable i.e. has a +1 verified and +2 Code Review. Options true or false                                                                                                                       | true                                                                     |
| WAIT_TIMEOUT_SEC_BEFORE_PUBLISH | The amount of time the script will wait for the review to become submittable, this is used when WAIT_SUBMITTABLE_BEFORE_PUBLISH is set to true                                                                                                                 | 1800                                                                     |
| CODE_REVIEW_ONLY                | If set to false a Verified +1 label and a Code-Review +2 label is applied to the review. If set to true, only a Code-Review +2 label is applied                                                                                                                | false                                                                    |
| GERRIT_USER_SECRET              | Jenkins secret ID with Gerrit username and password                                                                                                                                                                                                            | eoadm100-user-credentials                                                |
| TIMEOUT                         | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT          | The amount of time to wait in seconds for all the submodules to clone when executing the "gerrit clone" command                                                                                                                                                | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT        | The amount of time to wait in seconds when executing the "submodule update" command'                                                                                                                                                                           | 300                                                                      |
| ARMDOCKER_USER_SECRET           | Jenkins secret ID that stores the ARM Registry Credentials                                                                                                                                                                                                     | ciloopman-user-creds                                                      |
| SLAVE_LABEL                     | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE                 | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC                  | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

After a successful build, an artifact file is generated, gerrit_create_patch.properties.
The artifacts file will have a number of Gerrit related parameters associated to the review.

Example

```
GERRIT_URL=https://gerrit-gamma.gic.ericsson.se/#/c/123456789
GERRIT_CHANGE_NUMBER=123456789
GERRIT_REFSPEC=refs/changes/89/123456789/1
GERRIT_BRANCH=master
GERRIT_PATCHSET_NUMBER=1
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
  * **Script Path:** ci/jenkins/files/updateVersionInProductHelmfile.Jenkinsfile
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
