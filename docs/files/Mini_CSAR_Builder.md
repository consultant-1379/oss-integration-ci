# OSS Mini CSAR Builder Jenkins File

[TOC]

## Introduction

The OSS-Mini-CSAR-Builder Jenkins job is used to build the mini CSARs for all the charts that are currently in the helm file version specified in the Input Parameters of the OSS-Mini-CSAR-Builder Jenkins job. Also can be used to gather the site values and the optionality files into one location so it is easy to see what Applciation are setting within the site values and what applciation they wish to turn on.

## Overview

Currently, when the file is executed, it will

- The Jenkins job build will take input parameters; All parameters have defaults already populated except for the helm file version INT_CHART_VERSION, which is inputted by the user at build time. (All input parameters are listed in more detail below).
- The job then pulls down the helmfile version given. It uses this helmfile to get the application chart versions.
- The job creates mini CSARs that only include the integration chart and no actual docker images are included.
- The mini CSAR builder creates all the CSARs for the charts within the helmfile version inputted by the user.
- The mini CSAR builder will also build the helmfile CSAR if applicable for that helmfile.
- The CSARs are packaged into mini CSAR files and attached as artefacts and stored on the Jenkins build.
- These artifacts are stored on the build for 24hrs, and the Jenkins job will only keep the last 4 builds.
- Three files are also attached, that list all the optionality files and site values for the individual charts and the combined optionality file
**NOTE:** When using Mini CSAR then the docker registry in the site values file should be pointing to the global arm docker, not your local cluster docker registry.
```
global:
  registry:
    url: 'armdocker.rnd.ericsson.se'
    username: '<SET A USERNAME>'
    password: '<SET A PASSOWRD>'
```
### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/miniCsarBuilder.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml
- site-values/csar-build/miniCsar/site-values.yaml *(Site values file with tags set to true for each IDUN application mini csar to be built)*

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows.
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Mini-CSAR-Builder/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                     | Description                                                                                                                                                                                                                                                                                                                                                                                                  | Default                                                                    |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| INT_CHART_VERSION             | The version of the base platform helmfile to build mini CSARs from                                                                                                                                                                                                                                                                                                                                           |                                                                            |
| ARMDOCKER_USER_SECRET         | Jenkins Secret ID that stores the ARM Docker Credentials                                                                                                                                                                                                                                                                                                                                                     | ciloopman-docker-auth-config                                                |
| FULL_PATH_TO_SITE_VALUES_FILE | Full path within the Repo to the site_values.yaml file. Please choose the appropriate site values from the dropdown. Note: project reference in the directory structure. <br />IDUN Site Values: site-values/idun/ci/template/site-values-latest.yaml, <br />EO Site values: site-values/eo/ci/template/site-values-latest.yaml <br />EOOM Site values: site-values/eoom/ci/template/site-values-latest.yaml | site-values/idun/ci/template/site-values-latest.yaml                       |
| INT_CHART_NAME                | Integration Chart Name. Choose the appropriate helmfile name from the dropdown. <br />IDUN: eric-eiae-helmfile, <br />EO: eric-eo-helmfile <br />EOcCM: eric-eo-cm-helmfile <br />EOOM: eric-eoom-helmfile                                                                                                                                                                                                   | eric-eiae-helmfile                                                         |
| INT_CHART_REPO                | Integration Chart Repo. Choose the appropriate repo from the dropdown. Note EO VNFM & EO cCM repo has reference to eo in the url, same repo for both projects. The first and second option are for full helmfiles for IDUN and EO (VNFM & cCM), respectively. The third and fourth options are for snapshot helmfiles for IDUN and EO (VNFM & cCM), respectively.                                            | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local |
| FUNCTIONAL_USER_SECRET        | Jenkins secret ID that stores the ARM Registry Credentials                                                                                                                                                                                                                                                                                                                                                   | ciloopman-user-creds                                                        |
| TIMEOUT                       | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                                                                                                        | 3600                                                                       |
| SUBMODULE_SYNC_TIMEOUT        | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                                                                                                | 60                                                                         |
| SUBMODULE_UPDATE_TIMEOUT      | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                                                                                              | 300                                                                        |
| SLAVE_LABEL                   | Specify the slave label that you want the job to run on                                                                                                                                                                                                                                                                                                                                                      | evo_docker_engine                                                          |
| CI_DOCKER_IMAGE               | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                                                                                                                                                                  | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default   |
| GERRIT_REFSPEC                | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                                                                                                                                               | refs/heads/master                                                          |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

Upon a successful build the mini CSAR Artifacts are generated and attached to the Jenkins job at the end of the build.

The artifacts consist of .csar files of all the charts that are currently in the helm file version inputted at build time in the parameters.

Example of .csar files attached as a Jenkins artefacts:
```
eric-eiae-helmfile-1.1.1.csar
eric-cloud-native-base-21.0.0.csar
eric-eo-so-2.11.0-584.csar
eric-oss-adc-0.0.2-96.csar
eric-oss-app-mgr-1.1.0-59.csar
eric-oss-common-base-0.1.0-232.csar
eric-oss-config-handling-0.0.0-32.csar
eric-oss-dmm-0.0.0-44.csar
eric-oss-ericsson-adaptation-0.1.0-239.csar
eric-oss-pf-2.2.0-23.csar
eric-oss-uds-4.4.0-11.csar
eric-topology-handling-0.0.2-19.csar
```
Also, there are three files attached for troubleshooting,
  - individual_App_Optionality: This is a list of all the optionality files from the individual chart or helmfile as they are stored in the chart or helmfile
  - individual_App_SiteValues: This is all the site values from the individual chart or helmfile as they are stored in the chart or helmfile.
  - combined_optionality.yaml: This is all the optionality files merged into one overall file, similar to what Deployment Manager would create for a deployment.

Example of file
```
individual_App_Optionality.txt
individual_App_SiteValues.txt
combined_optionality.yaml
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
  * **Script Path:** ci/jenkins/files/miniCsarBuilder.Jenkinsfile
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
