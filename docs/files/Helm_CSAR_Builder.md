# OSS-CSAR-Builder Jenkins File

[TOC]

## Introduction

The OSS-CSAR-Builder Jenkins job is used to build the CSARs for the different helm components, base platform and OSS Applications.

## Overview
Currently, when the file is executed, it will
- take input parameters by the user.
- have some parameters as default values pre-populated.(All input parameters are listed in more detail below).
- take the helm chart info that is inputted as parameters, this is used to download the Chart.
- take a pre-populated site values file, which is fetched according to the SSH Repo Url given and any extra scripts that might be required.
- send the following items into the [CSAR Packaging Tool](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.orchestration.mgmt.packaging/am-package-manager/+/refs/heads/master/README.md) which builds the CSAR.
  * The name of the chart.
  * The actual chart to be built that's already downloaded as mentioned above.
  * The pre-populated site values file as mentioned in steps above.(This is an example of pre-populated site values file for the [UDS application](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.common.uds.service/uds-baseline/+/refs/heads/master/csar-build/uds/site-values/site-values.yaml))

> **Note:** Each application uses its own pre-populated site values file to template out their own chart, See the following link for more details [Introducing Application into EO chart or IDUN Helmfile](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/Introducing+Application+into+EO+chart+or+IDUN+Helmfile#IntroducingApplicationintoEOchartorIDUNHelmfile-CSARBuilds)

- Once built the CSAR is upload to the [Artifactory](https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/)

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/packaging/csar/helm/helmCsarBuilder.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows.
- [Jenkins Jobs](https://fem7s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-CSAR-Builder/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                         | Description                                                                                                                                                                                                                                                      | Default                                                                  |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_NAMES                   | Chart Name of Chart(s) to build from. Multiple charts can be included, using "," separation only. NOTE: The first chart name has to be the name of the CSAR.                                                                                                     |                                                                          |
| INT_CHART_VERSION                 | Version(s) of the Chart to build from. Multiple versions can be included, using "," separation only. NOTE: Versions should be in the same order as the Chart Name.                                                                                               |                                                                          |
| INT_CHART_REPOS                   | Repo(s) to fetch the chart from. Multiple repos can be included, using "," separation only. NOTE: Repos should be in the same order as the Chart Name.                                                                                                           |                                                                          |
| HELMFILE_CHART_NAME               | Name of the helmfile to be retrieved to run the helmfile template - e.g., eric-eiae-helmfile                                                                                                                                                                     |                                                                          |
| HELMFILE_CHART_VERSION            | The version of the helmfile to be retrieved to run the helmfile template                                                                                                                                                                                         |                                                                          |
| HELMFILE_CHART_REPO               | The repository to retrieve the helmfile                                                                                                                                                                                                                          |                                                                          |
| STATE_VALUES_FILE                 | The site-values file template to conduct the helmfile template                                                                                                                                                                                                   |                                                                          |
| PATH_TO_SITE_VALUES_OVERRIDE_FILE | The site-values override file to conduct the helmfile template                                                                                                                                                                                                   |                                                                          |
| SSH_REPO_URL                      | SSH URL to the repo that holds the pre-populated site values file and if required the scripts that should be included in the CSAR.                                                                                                                               |                                                                          |
| FORCE_CSAR_REBUILD                | Used to force a rebuild of the CSAR when set to true, even if there is a version already released into the ARM registry. Use with caution                                                                                                                        | false                                                                    |
| USE_TAG                           | Used to checkout the tag associates to the chart being built, to ensure the correct site values/scripts are used. If a tag is not found the master of the repo is checkout, If set to false then the checkout of the tag is skipped and we use what is on master | true                                                                     |
| USE_ERIC_PRODUCT_INFO             | Use --eric-product-info tag within the CSAR Builder to collect images from the eric-product-info.yaml instead of gathering images via the helm template command with given site-values file                                                                      | false                                                                    |
| SCRIPTS_DIR                       | Scripts directory within the SSH Repo URL specified. The content of this directory will be copied to the /scripts directory on the CSAR                                                                                                                          | None                                                                     |
| POPULATED_VALUES_FILE_LOCATION    | Full Path to the populated site values file within the SSH Repo URL (e.g. site-values/csar-build/config-handling/site-values.yaml). This file will be used to execute a helm template to get all the appropriate docker images to be included in the CSAR.       |                                                                          |
| CSAR_STORAGE_INSTANCE             | Storage Instance to push the CSARs to. NOTE: Use Default if unsure                                                                                                                                                                                               | arm.seli.gic.ericsson.se                                                 |
| CSAR_STORAGE_REPO                 | Storage directory to push the CSARs to. NOTE: Use Default if unsure                                                                                                                                                                                              | proj-eric-oss-drop-generic-local                                         |
| ARMDOCKER_USER_SECRET             | ARM Docker secret                                                                                                                                                                                                                                                |                                                                          |
| FUNCTIONAL_USER_SECRET            | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                   |                                                                          |
| TIMEOUT                           | Time to wait in seconds before the job should timeout                                                                                                                                                                                                            | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT            | Number of seconds before the submodule sync command times out                                                                                                                                                                                                    | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT          | Number of seconds before the submodule update command times out                                                                                                                                                                                                  | 300                                                                      |
| SLAVE_LABEL                       | Specify the slave label that you want the job to run on                                                                                                                                                                                                          | evo_docker_engine                                                        |
| DISTRIBUTION_EMAILS               | A list of emails to inform users if an existing CSAR is overwritten                                                                                                                                                                                              | PDLTICKETM@pdl.internal.ericsson.com                                     |
| CI_DOCKER_IMAGE                   | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                      | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC                    | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing   | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

This artifact.properties file will contain the CSAR created based off the inputs of the job when it runs.

Example:
```
INT_CHART_NAME=eric-oss-config-handling
INT_CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm
INT_CHART_VERSION=0.0.0-38
CSAR_STORAGE_INSTANCE=arm.seli.gic.ericsson.se
CSAR_STORAGE_REPO=proj-eric-oss-drop-generic-local
CSAR_STORAGE_LOCATION=csars/eric-oss-config-handling/0.0.0-38
CSAR_NAME=eric-oss-config-handling-0.0.0-38.csar
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
    * **Script Path:** ci/jenkins/files/packaging/csar/helm/helmCsarBuilder.Jenkinsfile
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
