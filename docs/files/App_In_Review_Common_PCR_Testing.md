# Application in Review Common PCR Testing File.

[TOC]

## Introduction

The job is used to execute the PCR against the given chart. It is triggered by a gerrit event when a chart is pushed for review.
This file works in conjunction with the [Common App Testing Jenkins file](Common_App_Test.md), both files need to exist.


## Overview
Currently, when the file is executed,
- The Jenkins job will take in parameters from the user (All Input Parameters are listed in more detail below).
- It will perform git clean of the workspace.
- It will then call a downstream job, to execute the Common App testing flow.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/app_test/pcr/appInReviewCommonPCRTest.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                        |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| APP_NAME                 | Application name, this is the name of the built chart, e.g. eric-oss-common-base-0.4.2-19.tgz --> ***eric-oss-common-base***                                                                                                                                   |                                |
| CHART_PATH               | Relative path to app chart in git repo.                                                                                                                                                                                                                        |                                |
| GIT_REPO_URL             | Gerrit https url to app git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart                                                                                                                                                          |                                |
| GERRIT_PROJECT           | Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base                                                                                                                                                                                               |                                |
| SCHEMA_TESTS_PATH        | The path to the directory containing the positive and negative schema files                                                                                                                                                                                    | testsuite/schematests/tests    |
| PATH_TO_SITE_VALUES_FILE | The path including file name of the site values file for templating the chart for the static test and design rule checking. The path should start from the root of the App chart repo.                                                                         | testsuite/site_values.yaml     |
| FULL_CHART_SCAN          | If "true" then the whole chart with its dependencies will be scanned.                                                                                                                                                                                          | false                          |
| GERRIT_USER_SECRET       | Jenkins secret ID with Gerrit username and password                                                                                                                                                                                                            |                                |
| ARMDOCKER_USER_SECRET    | Jenkins secret to log onto the Docker Arm                                                                                                                                                                                                                      |                                |
| HELM_REPO_CREDENTIALS_ID | Repositories.yaml file credential used for auth                                                                                                                                                                                                                |                                |
| USE_ADP_ENABLER          | Use a specific adp enabler to build the chart, two options available, adp-cihelm or adp-inca. Default adp-cihelm                                                                                                                                               | adp-cihelm                     |
| PCR_MASTER_JOB_NAME      | This is the common app testing job that will be trigged by this job to execute the test                                                                                                                                                                        | OSS-Integration-Common-Testing |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                           |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                             |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                            |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine              |
| CI_REFSPEC               | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master              |

>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

## Jenkins Job Configuration

> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be followed

- Create a new Pipeline Jenkins Job
- Within the "Build Triggers Section" of the Jenkins Job Configuration set the following
  * **Gerrit event:** Selected
  * **Trigger on:** Patchset Created
  * **Trigger on:** Draft Published

- Within the "Pipeline Section" of the Jenkins Job Configuration set the following
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** FETCH_HEAD
    * **Advanced - Refspec:** ${CI_REFSPEC}
    * **Advanced Behaviours - Advanced Clone Behaviours:** Honor refspec on initial clone
    * **Advanced Behaviours - Advanced Clone Behaviours:** Shallow Clone - Shallow Clone depth - 1
    * **Script Path:** ci/jenkins/files/app_test/pcr/appInReviewCommonPCRTest.Jenkinsfile
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
