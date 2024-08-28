# OSS Check Helmfile Deployment Jenkins File

[TOC]

## Introduction

This file can be used within a spinnaker flow to see can the initial install be skipped if all it's checks pass.
It checks the cluster that is specified within it's parameter, to ensure
 - The environment is in a good state i.e. none of the releases are in a failed state.
 - It ensures that the tags, that are sent in as parameter to the build, have the corresponding releases for the
 given deployment.
 - It ensures the environment is on the correct base i.e. ensure the applications version from the helmfile are deployed
  onto the system.

## Overview

Currently, when the file is executed it will

- Pulls down the helmfile version given. It uses this helmfile to get the application chart
 versions.
- Uses the tags set in the parameters it generates a dummy site values with those tags set.
- Using the dummy site values it gathers the details from the helmfile of what should be deployed.
- From the details gather from the helmfile it ensures,
    * All the appropriate release are deployed on the system.
    * Ensures all deployed releases are in a good state.
    * Ensures all deployed release versions match that of the specified helmfile.
> **Note:** For deployed releases that are not included within the specified Helmfile,
> the deployed release name should contain the prefix "internal-eric-test-<chart-name>"
> eg. "internal-eric-test-nels-simulator", this is to ensure the deployed release is removed within the comparison

- Output from the Jenkins file it will generate an artifact.properties. This will contain
    * A list of the all the releases and their version from the cluster specified.
    * A parameter, "SKIP_DELETION" set to true or false,
     If any of the test above fail it will be set to false.
     > All parameter in the outputted artifact.properties can be used by other stages in the flow as required.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/checkHelmfileDeployment.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset.yaml
- ci/jenkins/scripts/python-ci-scripts/src/check_helmfile_deployment_status.py *(Python script which holds all the functionality)*

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Check-Helmfile-Deployment-Status/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                                                 | Default                                                                  |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| NAMESPACE                | Namespace on the cluster that the deployment is installed into.                                                                                                                                                                                                                             |                                                                          |
| KUBECONFIG_FILE          | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                | kube_config.yaml                                                         |
| ENV_FILES_BUCKET_NAME    | Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data stored in OST.  See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                                                   |                                                                          |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                       | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                               | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                                             | 300                                                                      |
| SLAVE_LABEL              | Label of the Jenkins slave where this jenkins job should be executed.                                                                                                                                                                                                                       | evo_docker_engine                                                        |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                                                         | ciloopman-user-creds                                                      |
| INT_CHART_NAME           | Name of the Product Helmfile that is used to list the releases and their versions.                                                                                                                                                                                                          | eric-eiae-helmfile                                                       |
| INT_CHART_VERSION        | Version of the Product Helmfile used to fetch the correct helmfile from artifactory.                                                                                                                                                                                                        |                                                                          |
| INT_CHART_REPO           | Repo to use when fetching the helmfile.                                                                                                                                                                                                                                                     | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| PATH_TO_HELMFILE         | Location of the helmfile within the helmfile artifact that has been downloaded.                                                                                                                                                                                                             | eric-eiae-helmfile/helmfile.yaml                                         |
| TAGS                     | List of tags, used to ensure that the correct applications are deployed on the system with the correct version. Space separated list.                                                                                                                                                       | so pf uds adc th dmm eas                                                 |
| OPTIONAL_TAGS            | List of optional application tags (Example: SEF Application), used to ensure that the correct applications are deployed on the system with the correct version. Space separated list.                                                                                                       |                                                                          |
| OPTIONAL_KEY_VALUE_LIST  | Optional comma separated list of additional key/value pairs to be added to site values. Each key level should be separated by '.' and value by '=', e.g. eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false | None                                                                     |
| CHECK_TAGS               | List of specific tags to use for comparing deployed vs. helmfile chart-versions. Space separated list.                                                                                                                                                                                      | ''                                                                       |
| CHECK_FULL_VERSION       | Set to true if full chart version should be used instead of sprint version for application checks.                                                                                                                                                                                          | false                                                                    |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                                                 | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                              | refs/heads/master                                                        |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

The file holds the details of what is deployed on the system currently and a parameter stating if the redeploy should
be skipped or not. If all the test in a given run pass, then the SKIP_DELECTION parameter is set to true. Otherwise it
will be set to false, indicating that there is an issue with the specified deployment.

Example:
```
SKIP_DELETION=true
eric-cloud-native-base-21.0.0
eric-eo-so-2.11.0-584
eric-oss-adc-0.0.2-96
eric-oss-app-mgr-1.1.0-59
eric-oss-common-base-0.1.0-232
eric-oss-config-handling-0.0.0-32
eric-oss-dmm-0.0.0-44
eric-oss-ericsson-adaptation-0.1.0-239
eric-oss-pf-2.2.0-23
eric-oss-uds-4.4.0-11
eric-topology-handling-0.0.2-19
secret-eric-data-object-storage-mn-1.0.0
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
    * **Script Path:** ci/jenkins/files/checkHelmfileDeployment.Jenkinsfile
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
