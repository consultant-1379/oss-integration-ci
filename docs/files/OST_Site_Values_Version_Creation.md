# OST Site Values Version Creation Jenkins File

[TOC]

## Introduction

This script is used to store a new site values with a product version according to the parameter inputted into the job.

## Overview

Currently, when the file is executed it will:

- It checks does the version already exist

- It fetches the site values that are set in the SITE_VALUES_FILE_LATEST and the SITE_VALUES_FILE_LATEST_BUCKET_NAME
parameters

- Creates a new site values with a version according to parameter, "HELMFILE_VERSION".

- It uploads the created site value to a bucket set in the "SITE_VALUES_FILE_VERSIONED_BUCKET_NAME" parameter

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/inventory/ost/site_values_version_creation.Jenkinsfile
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-OST-Site-Values-Version-Creation/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                              | Description                                                                                                                                                                                                                                                    | Default                 |
|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| HELMFILE_NAME                          | Project Helmfile Name.                                                                                                                                                                                                                                         |                         |
| HELMFILE_VERSION                       | Project Helmfile Version.                                                                                                                                                                                                                                      |                         |
| SITE_VALUES_FILE_LATEST                | Name of the site values template to use to create the versioned site values from, including the file extension                                                                                                                                                 | site-values-latest.yaml |
| SITE_VALUES_FILE_LATEST_BUCKET_NAME    | Name of the bucket that is storing the site values file latest that is stored in object store.                                                                                                                                                                 |                         |
| SITE_VALUES_FILE_VERSIONED_BUCKET_NAME | Name of the bucket that is storing the site values versioned version that will be stored in object store.                                                                                                                                                      |                         |
| FUNCTIONAL_USER_SECRET                 | Functional user that has access to all appropriate buckets in object store. The user creds should be stored in the Jenkins credentials area.                                                                                                                   |                         |
| ARMDOCKER_USER_SECRET                  | ARM Docker secret that is stored in the Jenkins credentials area.                                                                                                                                                                                              | 3600                    |
| SUBMODULE_SYNC_TIMEOUT                 | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                      |
| SUBMODULE_UPDATE_TIMEOUT               | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                     |
| AGENT_LABEL                            | Specify the agent label that you want the job to run on.                                                                                                                                                                                                       | evo_docker_engine       |
| GERRIT_REFSPEC                         | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master       |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

None

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
    * **Script Path:** ci/jenkins/files/inventory/ost/site_values_version_creation.Jenkinsfile
> **Note:** In order for the pipeline to work, the Credentials plugin should be installed and have the appropriate
> credentials created.

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
