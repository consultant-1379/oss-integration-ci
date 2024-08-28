# OSS Gerrit Notification Jenkins File

[TOC]

## Introduction

This file is used in order to return the status of a job to Gerrit History.

The message that is returned to Gerrit message can then be viewed within Gerrit History.

## Overview

Currently, when the file is executed it will:

- Using the parameters entered (Message, GERRIT_CHANGE_NUMBER, GERRIT_PATCHSET_NUMBER) the Gerrit Review Command is executed.


- The Gerrit Review Command executed appends the Message parameter to the PatchSet specified at /GERRIT_CHANGE_NUMBER/GERRIT_PATCHSET_NUMBER.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/gerritNotification.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Common-Base-Gerrit-Notification/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter              | Description                                                                                                                                                                                                                                                    | Default           |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| Message                | A message to be added as feedback on the triggering Gerrit event.                                                                                                                                                                                              |                   |
| LABEL                  | A verification label used in the case of the test flow failing.                                                                                                                                                                                                |                   |
| GERRIT_CHANGE_NUMBER   | Parameter name for the change number.                                                                                                                                                                                                                          |                   |
| GERRIT_PATCHSET_NUMBER | Parameter name for the patch set number.                                                                                                                                                                                                                       |                   |
| SLAVE_LABEL            | Specify the slave label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine |
| TIMEOUT                | Time to wait in seconds before the job should timeout.                                                                                                                                                                                                         | 3600              |
| GERRIT_REFSPEC         | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

No output file/artifact is created when this Jenkins File has finished executing.

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
    * **Script Path:** ci/jenkins/files/gerritNotification.Jenkinsfile
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
