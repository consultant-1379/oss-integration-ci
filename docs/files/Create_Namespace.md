# OSS Create a new namespace within the given cluster

[TOC]

## Introduction

This file can be used within a spinnaker flow to create a new namespace within the cluster according to the input parameters below.

## Overview

Currently, when the file is executed it will:


- Takes in the 5 input parameters discussed down below.


- The jenkins file will execute a kubectl command against the cluster to create the given namespace.
Depending on the parameters inputted the script will either ignore the namespace being already created
(i.e. crd namespaces) or will fail the jenkins file if it is already created.


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/pre-deploy/create-namespace.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem7s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-predeploy-create-namespace/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| NAMESPACE                | The namespace name to be created.                                                                                                                                                                                                                              | oss-deploy                                                               |
| KUBECONFIG_FILE          | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.   | kube_config.yaml                                                         |
| ENV_FILES_BUCKET_NAME    | Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data stored in OST.  See [OST File Bucket](OST_Deployment_Files_Bucket_Generation.md) for details.                                      | None                                                                     |
| FUNCTIONAL_USER_SECRET   | ID of the Function User that has been stored on the Jenkins server in the credentials area as a username and password, see [credential storage](Credentials_Storage.md) for details                                                                            |                                                                          |
| IGNORE_IF_CREATED        | Used to ignore if the namespace is already created do not fail the job. Set to true or false                                                                                                                                                                   | false                                                                    |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

#### Output File

There are no files output from the job.

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
    * **Script Path:** ci/jenkins/files/pre-deploy/create-namespace.Jenkinsfile
> **Note:**  * In order to make this pipeline work, the following configuration on Jenkins is required: slave with a specific label (see pipeline.agent.label below)

> **Note:** In order for the pipeline to work, the kubernetes config should be added to the Jenkins Credentials: e.g. c12a011-config-file (kube config file to access c12a011 cluster)

> **Note:** Once the Jenkins job has been configured with as above, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though first time around.

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
