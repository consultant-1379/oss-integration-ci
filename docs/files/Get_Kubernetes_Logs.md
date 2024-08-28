# OSS Get Kubernetes Logs Jenkins File

[TOC]

## Introduction
This file can be used within a spinnaker flow to gather the logs for a specific environment.

The deployment manager is used within this script in order to collect the logs found (Via the helm get and logs_commands methods) and to also store these logs within a volume during execution.

Application logs can help you understand what is happening inside your application. The logs are particularly useful for debugging problems and monitoring cluster activity.

## Overview

Currently, when the file is executed it will:

- Create a subdirectory in the current directory named kube_config.


- The KUBECONFIG (KUBECONFIG_FILE) file is copied to ./kube_config/config with full write permissions.


- The gather-deployment-logs function is called which collects logs from the deployment manager docker image for the specified namespace.


- A log.tgz file containing the log information of the Kubernetes environment (It is possible that this logs file could be empty if no Cluster is found).

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/getKubernetesLogs.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Get-K8S-logs/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                     | Default                     |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|
| NAMESPACE                | Namespace to install the Chart.                                                                                                                                                                                                                                 |                             |
| ARMDOCKER_USER_SECRET    | ARM Docker secret.                                                                                                                                                                                                                                              | ciloopman-docker-auth-config |
| KUBECONFIG_FILE          | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.    | kube_config.yaml            |
| ENV_FILES_BUCKET_NAME    | Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data stored in OST.  See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                       | None                        |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                             |                             |
| COLLECT_LOGS_WITH_DM     | If set to "false" (by default) - logs will be collected by ADP logs collection script. If true - with deployment-manager tool.                                                                                                                                  | false                       |
| PATH_TO_AWS_FILES        | Path within the Repo to the location of the AWS credentials and config directory.                                                                                                                                                                               | NONE                        |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                   | 60                          |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                 | 300                         |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                        | evo_docker_engine           |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing. | refs/heads/master           |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

#### Output File

A log TAR archive is generated and attached to the Jenkins execution at the end of the flow.

This Archive file will contain the logs which were collected from the Kubernetes environment.

This logs will include the helm deployments on the Kubernetes cluster (Within the helm folder), the logs for each Docker Application (Within the logs folder) and the Kubernetes Cluster Information (Such as Role-Bindings, Secrets, Jobs, Pods, Nodes, Persistent Volumes etc.).

Example:
```
# Log TAR archive which contains the logs of the Kubernetes Cluster

# TAR archive outputted:
  logs_oss-deploy_2022-01-24-11-01-43.tgz
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
  * **Script Path:** ci/jenkins/files/getKubernetesLogs.Jenkinsfile
> **Note:** In order for the pipeline to work, the Credentials plugin should be installed and have the following secret: c12a011-config-file (admin.config to access c12a011 cluster)

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
