# OSS Gather Environment Details Jenkins File

[TOC]

## Introduction

This file can be used within a spinnaker flow to gather the environment details for a specific environment.

## Overview

Currently, when the file is executed it will:

- Using the parameters entered, .conf is appended to the end of the environment name given (Which will be used to search for the config file for the specific environment <ENV_NAME> in order to retrieve the environment variables within the environment details directory <ENV_DETAILS_DIR>).


- The current repository is used to search for the config file previously mentioned, if the file exists Jenkins will add the environment variables found in the config file to the artifact.properties file.


- Using the output from the Jenkins file it will generate an artifact.properties. This file will contain a list of all the environment variable keys that were found in the config file for the given environment, with their corresponding values.
  > All parameters in the outputted artifact.properties can be used by other stages in the flow as required.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/gatherEnvDetails.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml


### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Gather-Env-Details/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                        |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| USE_DIT                  | Set to true or false, if set to true will fetch the environment details from the Deployment Inventory Tool (DIT). See [deployment storage using DIT](DIT_Deployment_Generation.md) for more details                                                            |                                |
| ENV_NAME                 | Name of the Environment to Gather details for. This should match your pooled environment in RPT or Jenkins lockable resources.                                                                                                                                 |                                |
| ENV_DETAILS_DIR          | Location to search for environment details associated to the the ENV_NAME.                                                                                                                                                                                     | honeypots/pooling/environments |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                            |                                |
| SPINNAKER_PIPELINE_ID    | ID of the associated Spinnaker pipeline. Used as a placeholder in order to mitigate Jenkins 404 errors.                                                                                                                                                        | 123456                         |                                                                                                                                                                                                                                                               |                                                                              |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                           |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                             |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                            |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine              |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master              |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow.

This file holds the details of the environment variables (as key-value pairs) which were obtained through the config file of the environment given, found within the environment details directory.

Example:
```
# File that specifies the Environment details.

# Configuration file location in CI REPO
PATH_TO_CERTIFICATES_FILES=honeypots/ci/environment/hall912/certificates
KUBE_CONFIG=hall912-config-file
PLATFORM=KaaS

# Cluster details
NAMESPACE=oss-deploy

# Hostname for the Deployment
EO_VNFM_HOSTNAME=vnfm.hall912.rnd.gic.ericsson.se
EO_SO_HOSTNAME=so.hall912.rnd.gic.ericsson.se
EO_PF_HOSTNAME=pf.hall912.rnd.gic.ericsson.se
EO_UDS_HOSTNAME=sdd.hall912.rnd.gic.ericsson.se
EO_VNFM_REGISTRY_HOSTNAME=registry.hall912.rnd.gic.ericsson.se
IAM_HOSTNAME=keycloak.hall912.rnd.gic.ericsson.se
EO_GAS_HOSTNAME=gas.hall912.rnd.gic.ericsson.se
EO_ADC_HOSTNAME=adc.hall912.rnd.gic.ericsson.se
EO_APPMGR_HOSTNAME=appmgr.hall912.rnd.gic.ericsson.se
EO_DMM_HOSTNAME=dmm.hall912.rnd.gic.ericsson.se
EO_HELM_REGISTRY_HOSTNAME=default

#ICCR
PATH_TO_CERTIFICATES_FILES_ICCR=honeypots/ci/environment/hall912/iccr
EO_VNFM_HOSTNAME_ICCR=vnfm.hall912-iccr.ews.gic.ericsson.se
EO_SO_HOSTNAME_ICCR=so.hall912-iccr.ews.gic.ericsson.se
EO_PF_HOSTNAME_ICCR=pf.hall912-iccr.ews.gic.ericsson.se
EO_UDS_HOSTNAME_ICCR=sdd.hall912-iccr.ews.gic.ericsson.se
EO_VNFM_REGISTRY_HOSTNAME_ICCR=registry.hall912-iccr.ews.gic.ericsson.se
IAM_HOSTNAME_ICCR=keycloak.hall912-iccr.ews.gic.ericsson.se
EO_GAS_HOSTNAME_ICCR=gas.hall912-iccr.ews.gic.ericsson.se
EO_ADC_HOSTNAME_ICCR=adc.hall912-iccr.ews.gic.ericsson.se
EO_APPMGR_HOSTNAME_ICCR=appmgr.hall912-iccr.ews.gic.ericsson.se
EO_DMM_HOSTNAME_ICCR=dmm.hall912-iccr.ews.gic.ericsson.se
ICCR_IP=10.158.33.185
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
  * **Script Path:** ci/jenkins/files/gatherEnvDetails.Jenkinsfile
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
