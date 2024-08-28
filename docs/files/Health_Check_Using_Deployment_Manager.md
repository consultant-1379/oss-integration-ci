# OSS Health Check using Deployment Manager

## Introduction

This jenkinsfile is used to execute a health check of the deployment prior to executing an
- Upgrade Install
- Backup of the System Data

The Deployment manager Health check, provides a snapshot view of health of workloads/network/storage
in the deployed kubernetes cluster.

**Note:** This functionality was introduced into Deployment manager version, 1.41.0-56 or higher.

## Overview

Currently, when the file is executed it will

- Pulls down the deployment manager docker image.

- Executes the Health check command within deployment manager to perform the check on "all"
kubernetes services.

- The following Health check command is executed: "health-check all -n <namespace>"

- Once the script is executed a decision is made to fail or to pass the job, according to
the output from the command, if the following sentence is found the job passes, "command completed
successfully with no failure"

- All the output from the command can be found in the console of the Jenkins job.

## Resources

- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-HealthCheck-Using-DM/)

## Prerequisite

To be able to use this Jenkins job the following needs to be fulfilled

- Kube Config File added to Jenkins within the Credentials Section.

**NOTE** Make sure the Kube config file has the correct API key so that it can be accessed as external
 to the Director.
The Kube config file should be stored in Jenkins credentials as a "Secret File" and the ID given to the
 file can be used within the Jenkins job for the parameter.

- ARM Docker User Secret added to Jenkins within the Credentials Section. This is needed to pull the
 Deployment Manager image

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/healthCheckUsingDeploymentManager.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Defaults            |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| NAMESPACE                | Namespace to execute the check against                                                                                                                                                                                                                         |                     |
| KUBECONFIG_FILE          | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.   | kube_config.yaml    |
| ENV_FILES_BUCKET_NAME    | Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data stored in OST.  See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                      | None                |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                  |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                 |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine   |
| ARMDOCKER_USER_SECRET    | ARM Docker secret ID that was stored in the Jenkins credentials area                                                                                                                                                                                           |                     |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                 | ciloopman-user-creds |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master   |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

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
    * **Script Path:** ci/jenkins/files/healthCheckUsingDeploymentManager.Jenkinsfile
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
