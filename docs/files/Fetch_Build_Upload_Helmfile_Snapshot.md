# OSS Integration Fetch, build & upload Helmfile Snapshot Jenkins file

[TOC]

## Introduction

This file is used to generate a Helmfile artifact which can be used in the different testing phases.
It can be used to generate a snapshot only of the artifact - not a releasable artifact.

## Overview

Currently, when the file is executed it will:

- Clean down the Jenkins workspace before starting a new test flow.
- Downloads the artifact repo to a tmp location
- Checks what version should be used next.
- Upload the generated package to the appropriate repo
- Tags the repo with the appropriate version for tracking


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/packaging/helmfile/fetchBuildUploadHelmfileSnapshot.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml
- internal/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following job is used within the Base flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Helmfile-Fetch-Build-Upload/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Default           |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| GERRIT_USER_SECRET           | Jenkins secret ID with Gerrit username and password.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                   |
| FUNCTIONAL_USER_TOKEN        | Jenkins secret token ID for ARM Registry Token.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                   |
| GERRIT_REFSPEC               | Gerrit refspec of the app under tests example: refs/changes/88/9999988/9 - 88 - last 2 digits of Gerrit commit number / 9999988 - is Gerrit commit number / 9 - patch number of gerrit commit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                   |
| CHART_NAME                   | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg'. Used to find the specific chart name in the Chart.yaml to swap the correct version for the service. GERRIT_REFSPEC should be blank if using this value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                   |
| CHART_VERSION                | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57. Used to swap out the version according to the CHART_NAME specified in the Chart.yaml. GERRIT_REFSPEC should be blank if using this value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                   |
| CHART_REPO                   | Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2'. GERRIT_REFSPEC should be blank if using this value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                   |
| GERRIT_PROJECT               | Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |                   |
| CHART_PATH                   | Relative path to app chart in git repo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                   |
| HELM_INTERNAL_REPO           | Repository to upload the snapshot version to.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                   |
| SPINNAKER_PIPELINE_ID        | ID of the associated Spinnaker pipeline. Used as a placeholder in order to mitigate Jenkins 404 errors.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 123456            |
| VCS_BRANCH                   | Branch for the change to be pushed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | master            |
| STATE_VALUES_FILE            | Relative path to the Site values file that is used for the helmfile build, this pre-populated file can be found in the oss-integration-ci repo, <br> e.g. <br> [EO Prepopulated file](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/site-values/eo/ci/override/override-site-values-helmfile-template.yaml) : site-values/eo/ci/override/override-site-values-helmfile-template.yaml <br> [EIC Prepopulated file](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/site-values/idun/ci/override/override-site-values-helmfile-template.yaml) : site-values/idun/ci/override/override-site-values-helmfile-template.yaml | None              |
| ALLOW_DOWNGRADE              | Default is 'false', if set to true, downgrade of dependency is allowed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | false             |
| VERSION_CHECK_DOWNGRADE      | Default is 'false', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | false             |
| VERSION_STEP_STRATEGY_MANUAL | Possible values: MAJOR, MINOR, PATCH. Step this digit automatically in Chart.yaml after release when manaul change received. Default is MINOR.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | MINOR             |
| ARTIFACT_UPLOAD_TO_ARM       | If set to true, will upload the artifact to the specified ARM repository, else it will be attached to the jenkins job as an artifact for local testing.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | true              |
| TIMEOUT                      | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 3600              |
| SUBMODULE_SYNC_TIMEOUT       | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 60                |
| SUBMODULE_UPDATE_TIMEOUT     | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 300               |
| SLAVE_LABEL                  | Specify the slave label that you want the job to run on.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | evo_docker_engine |
| CI_REFSPEC                   | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | refs/heads/master |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

On a successful execution an artifact.properties file is created - this artifact lists the details of the created snapshot.

e.g. if CHART_NAME, CHART_REPO and CHART_VERSION are used for the snapshot

```
INT_CHART_NAME=eric-eiae-helmfile
INT_CHART_VERSION=2.2156.1-1-197d0a8
INT_CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm
INT_CHART_NAME_STABLE=None
INT_CHART_VERSION_STABLE=None
INT_CHART_REPO_STABLE=None
CHART_NAME=eric-oss-common-base, eric-cncs-oss-config
CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
CHART_VERSION=0.396.0, 0.49.0
TYPE_DEPLOYMENT=prepare
```

e.g. if a refspec is used for the snapshot

```
INT_CHART_NAME=eric-eiae-helmfile
INT_CHART_VERSION=2.2161.1-1-c66a5d71
INT_CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm
INT_CHART_NAME_STABLE=None
INT_CHART_VERSION_STABLE=None
INT_CHART_REPO_STABLE=None
GERRIT_REFSPEC=refs/changes/73/17243873/1
TYPE_DEPLOYMENT=prepare
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
    * **Script Path:** ci/jenkins/files/packaging/helmfile/fetchBuildUploadHelmfileSnapshot.Jenkinsfile
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
