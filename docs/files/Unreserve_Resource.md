# Unreserve Environment Jenkins File

[TOC]

## Introduction

This file is primarily used by the product staging spinnaker flows to unreserved environments that are no longer needed as part of a flow.
There is several testing pipelines and flows that will need to reserve and unreserve environments in order to run their flow.
While an environment is reserved, other flows will wait for an environment to become available before continuing. This stops spinnaker flows
and jenkins jobs from conflicting with each.The purpose of this file is to provide a jenkins job that can unreserve an environment once the given environment is no longer needed by a given flow.

Note: In order to run a Jenkins job using this Jenkinsfile, your Jenkins server will need to have the Lockable Resources plugin installed.
To check to see if the Lockable Resources is installed on your cluster, you can check via using to the following url:
https://<YOUR_JENKINS_URL>/jenkins/lockable-resources/
You should see the Lockable Resources your jenkins server has stored on it. You may need admin access to see this page however.
If you don't have the Lockable Resources plugin installed, please contact your jenkins admin and request to have the Lockable
Resources plugin installed and configured to hold a variable for your environment. Please refer to the Lockable Resources
plugin documentation on how to correctly do this.

## Overview

Currently, when this file executes, it will:

- take in the input parameters (listed in more detail below).
- use the jenkins plugin, Lockable Resources, to check if the given environment is reserved or not.
  If the environment is not reserved, it will unreserve it.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/unreserveResource.Jenkinsfile *(Main Jenkins File)*

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Unreserve-Environment/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter      | Description                                                                                                                                                                                                                                                    | Default           |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| ENV_NAME       | Name of the Environment to be unreserved                                                                                                                                                                                                                       | None              |
| SLAVE_LABEL    | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine |
| TIMEOUT        | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600              |
| GERRIT_REFSPEC | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

There is no Output File for this jenkins job.

## Jenkins Job Configuration

> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be done

- Create a new Pipeline Jenkins Job
- Within the "Pipeline" Section of the Jenkins Job Configuration set the following:
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** master
    * **Script Path:** ci/jenkins/files/unreserveResource.Jenkinsfile
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
