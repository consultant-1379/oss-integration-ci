# OSS UDS Backend Job Wait Jenkins File

[TOC]

## Introduction

This pipeline is used to wait for a specified Job to complete within the time given.

## Overview

Currently, when the file is executed it will:

- Take in 5 parameters discussed in detail below.


- The KUBECONFIG (KUBECONFIG_FILE) is copied to admin.conf within the current directory.


- The eric-oss-ci-scripts image is installed in order to execute the wait specified down below.


- The uds-backend-job-wait target is executed which will wait the specified time for the indicated Job to complete.


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/udsBackendJobWait.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/scripts/python-ci-scripts
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/UDS-backend-wait/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                 |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| NAMESPACE                | Namespace to purge and delete the PVCs.                                                                                                                                                                                                                        | eo                                      |
| KUBECONFIG_FILE          | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.   | kube_config.yaml                        |
| ENV_FILES_BUCKET_NAME    | Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data stored in OST.  See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                      | None                                    |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                            |                                         |
| TIME                     | Time value to wait for. An integer plus a time unit s (seconds) m (minutes) h (hours)                                                                                                                                                                          | 1800s                                   |
| JOB                      | Specify job to watch during the wait.                                                                                                                                                                                                                          | eric-oss-uds-service-config-backend-job |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                      |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                     |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine                       |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                       |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

#### Output File

There is no file outputted for this Jenkins job.

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
    * **Script Path:** ci/jenkins/files/udsBackendJobWait.Jenkinsfile
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