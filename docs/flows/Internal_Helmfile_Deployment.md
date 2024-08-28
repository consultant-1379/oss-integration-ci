# Internal Helmfile Deployment

> **Note:** This spinnaker flow is used internally by Ticketmaster.

[TOC]

## Introduction

This spinnaker flow can be used to deploy a Product Helmfile on an environment.
This can be done by building and uploading a snapshot of oss-common-base from a Gerrit Ref Spec, which is then used to build and deploy a snapshot of a Product Helmfile.
It can also be done by building and uploading a snapshot of the Helmfile from a Helmfile Gerrit Ref Spec.
The steps are:
- OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec
    * Fetches the commit, builds the snapshot and uploads it to the specified repo
- Set Variables for OSS Common Chart Details from Gerrit Ref Spec
    * Extracts the chart name, version and repo and what changed from the Ref Spec
- Check Preconditions
    * Checks if the "Set Variables for OSS Common Chart Details from Gerrit Ref Spec" stage has succeeded or was skipped
- EIC Helmfile Fetch Build Upload
    * Build and upload the EIC Helmfile snapshot including the App Chart snapshot generated previously
- EIC Helmfile Fetch Build Upload Snapshot From Ref Spec
    * Build and upload the EIC Helmfile snapshot from a Helmfile Refspec
- EO Helmfile Fetch Build Upload
    * Build and upload the EO Helmfile snapshot including the App Chart snapshot generated previously
- EO Helmfile Fetch Build Upload Snapshot From Ref Spec
    * Build and upload the EO Helmfile snapshot from a Helmfile Refspec
- Evaluate Variables From EIC Helmfile Built From App Chart
    * Extracts the chart name, version and repo from the EIC Helmfile Fetch Build Upload stage
- Evaluate Variables From EIC Helmfile Built From Ref Spec
    * Extracts the chart name, version and repo from the EIC Helmfile Fetch Build Upload stage
- Evaluate Variables From EO Helmfile Built From App Chart
    * Extracts the chart name, version and repo from the EO Helmfile Fetch Build Upload stage
- Evaluate Variables From EO Helmfile Built From Ref Spec
    * Extracts the chart name, version and repo from the EO Helmfile Fetch Build Upload stage
- Reserve Environment
    * Reserves an environment for the deployment using the specified label
- Gather Env Details
    * Extract the required environment details for the deployment
- Purge Namespace
    * Clean down resources previously deployed in the namespace
- IDUN Pre Deployment
    * Creates namespaces, secrets and cluster role bindings for an EIC deployment
- EO Pre Deployment
    * Creates namespaces, secrets and cluster role bindings for an EO deployment
- Install using Helmfile
    * Install the Helmfile using the snapshot created previously
- Unreserve Namespace
    * Release the environment from lockable resources, so it can be reused

It flows as follows:
- If the GERRIT_REFSPEC global parameter is set to an oss-common-base ref spec, then the built snapshot of this ref spec is incorporated into the Helmfile. Otherwise, the building of this chart is skipped.
- If the building of the application chart is skipped, and the HELMFILE_GERRIT_REFSPEC global parameter is set to a Helmfile ref spec, then that ref spec will be used to build the Helmfile.
- If the HELMFILE_TYPE global parameter is set to EIC, then the flow will follow the path of deploying EIC.
- If the HELMFILE_TYPE global parameter is set to EO, then the flow will follow the path of deploying EO.


### Resources

The following is a link to the spinnaker flow
- [Internal Helmfile Deployment](https://spinnaker.rnd.gic.ericsson.se/#/projects/ticketmaster-e2e-cicd/applications/common-cicd/executions?pipeline=Internal-Helmfile-Deployment)


## Stage Overview

This is an overview of the stages, the parameters used for each section:

- OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec
    * Runs based on a conditional expression, i.e., GERRIT_REFSPEC != 'None'
    * Fetches the commit, builds the snapshot and uploads it to the specified repo
    * Uses the submitCode job of the oss-integration-ci repo [submitCode.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/submitCode.Jenkinsfile)
    * Please refer to the job in the point above for the updated list of parameters


- Set Variables for OSS Common Chart Details from Gerrit Ref Spec
    * Runs based on the condition that the OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec stage "SUCCEEDED"
    * Extracts the chart name, version and repo and what changed from the Ref Spec
      ```
      Variables               Values used to extract them

      INT_CHART_NAME          ${#stage("OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec")["context"]["INT_CHART_NAME"]}
      INT_CHART_VERSION       ${#stage("OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec")["context"]["INT_CHART_VERSION"]}
      INT_CHART_REPO          ${#stage("OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec")["context"]["INT_CHART_REPO"]}
      WHAT_CHANGED            OSS
      ```

- Check Preconditions
    * Runs based on the condition that the OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec stage "SUCCEEDED"
    * Checks if the "Set Variables for OSS Common Chart Details from Gerrit Ref Spec" stage has succeeded or was skipped
      ```
      Expression

       "${#stage('Set Variables for OSS Common Chart Details from Gerrit Ref Spec')['status']}" == "SUCCEEDED" or
       "${#stage('Set Variables for OSS Common Chart Details from Gerrit Ref Spec')['status']}" == "SKIPPED"
      ```

- EIC Helmfile Fetch Build Upload
    * Runs based on the condition that the Check Preconditions stage "SUCCEEDED"
    * Builds the Helmfile snapshot, incorporating the chart built from the OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec stage
    * Uses the submitCode job of the Helmfile [submitCode.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/refs/heads/master/ci/jenkins/files/submitCode.Jenkinsfile)
    * Please refer to the job in the point above for the updated list of parameters


- EIC Helmfile Fetch Build Upload Snapshot from Ref Spec
    * Runs based on the condition that the Check Preconditions stage was "SKIPPED"
    * Fetches the commit, builds the snapshot and uploads it to the specified repo
    * Uses the submitCode job of the Helmfile [submitCode.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/refs/heads/master/ci/jenkins/files/submitCode.Jenkinsfile)
    * Please refer to the job in the point above for the updated list of parameters


- EO Helmfile Fetch Build Upload
    * Runs based on the condition that the Check Preconditions stage "SUCCEEDED"
    * Builds the Helmfile snapshot, incorporating the chart built from the OSS COMMON BASE Fetch, Build and Upload from Gerrit Ref Spec stage
    * Uses the submitCode job of the Helmfile [submitCode.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eo/eo-helmfile/+/master/ci/jenkins/files/submitCode.JenkinsFile)
    * Please refer to the job in the point above for the updated list of parameters


- EO Helmfile Fetch Build Upload Snapshot From Ref Spec
    * Runs based on the condition that the Check Preconditions stage "SUCCEEDED"
    * Fetches the commit, builds the snapshot and uploads it to the specified repo
    * Uses the submitCode job of the Helmfile [submitCode.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eo/eo-helmfile/+/master/ci/jenkins/files/submitCode.JenkinsFile)
    * Please refer to the job in the point above for the updated list of parameters


- Evaluate Variables from EIC Helmfile Built from App Chart
    * Runs based on the condition that the EIC Helmfile Fetch Build Upload stage "SUCCEEDED"
    * Extracts the helmfile snapshot's name, version and repo outputted from the Helmfile Fetch Build Upload Snapshot from Ref Spec stage
      ```
      Variables Outputted      Values used to extract them

      INT_CHART_NAME           ${#stage("EIC Helmfile Fetch Build Upload")["context"]["INT_CHART_NAME"]}
      INT_CHART_VERSION        ${#stage("EIC Helmfile Fetch Build Upload")["context"]["INT_CHART_VERSION"]}
      INT_CHART_REPO           ${#stage("EIC Helmfile Fetch Build Upload")["context"]["INT_CHART_REPO"]}
      ```

- Evaluate Variables from EIC Helmfile Built from Ref Spec
    * Runs based on the condition that the EIC Helmfile Fetch Build Upload Snapshot from Ref Spec stage "SUCCEEDED"
    * Extracts the helmfile snapshot's name, version and repo outputted from the Helmfile Fetch Build Upload Snapshot from Ref Spec stage
      ```
      Variables Outputted      Values used to extract them

      INT_CHART_NAME           ${#stage("EIC Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_NAME"]}
      INT_CHART_VERSION        ${#stage("EIC Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_VERSION"]}
      INT_CHART_REPO           ${#stage("EIC Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_REPO"]}
      ```

- Evaluate Variables from EO Helmfile Built from App Chart
    * Runs based on the condition that the EO Helmfile Fetch Build Upload stage "SUCCEEDED"
    * Extracts the helmfile snapshot's name, version and repo outputted from the Helmfile Fetch Build Upload Snapshot from Ref Spec stage
      ```
      Variables Outputted      Values used to extract them

      INT_CHART_NAME           ${#stage("EO Helmfile Fetch Build Upload")["context"]["INT_CHART_NAME"]}
      INT_CHART_VERSION        ${#stage("EO Helmfile Fetch Build Upload")["context"]["INT_CHART_VERSION"]}
      INT_CHART_REPO           ${#stage("EO Helmfile Fetch Build Upload")["context"]["INT_CHART_REPO"]}
      ```

- Evaluate Variables from EO Helmfile Built from Ref Spec
    * Runs based on the condition that the EO Helmfile Fetch Build Upload Snapshot from Ref Spec stage "SUCCEEDED"
    * Extracts the helmfile snapshot's name, version and repo outputted from the Helmfile Fetch Build Upload Snapshot from Ref Spec stage
      ```
      Variables Outputted      Values used to extract them

      INT_CHART_NAME           ${#stage("EO Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_NAME"]}
      INT_CHART_VERSION        ${#stage("EO Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_VERSION"]}
      INT_CHART_REPO           ${#stage("EO Helmfile Fetch Build Upload Snapshot from Ref Spec")["context"]["INT_CHART_REPO"]}
      ```

- Reserve Environment
    * Reserve an environment for carrying out the deployment
    * Uses the reserveResource Jenkins job [reserveResource.jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/reserveResource.Jenkinsfile)
    * More information about this job can be found at [reserveResource.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/reserveResource.md)
    * Please refer to the job and documentation in the points above for the updated list of parameters


- Gather Environment Details
    * Extract the environment details needed for the deployment
    * Uses the gatherEnvDetails Jenkins job [gatherEnvDetails.jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/gatherEnvDetails.Jenkinsfile)
    * More information about this job can be found at [gatherEnvDetails.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/gatherEnvDetails.md)
    * Please refer to the job and documentation in the points above for the updated list of parameters


- Purge Namespace
    * Clean down resources previously deployed in the namespace
    * Uses the purge Jenkins job [purge.jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/purge.Jenkinsfile)
    * More information about this job can be found at [purge.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/purge.md)
    * Please refer to the job and documentation in the points above for the updated list of parameters


- IDUN Pre Deployment
    * This stage breaks off into a different pipeline execution, the IDUN-Pre-Deployment pipeline
    * The Spinnaker flow covers the pre steps from the IDUN Deployment document.
    * More information about this pipeline can be found at [IDUN-Pre-Deployment.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/flows/IDUN-Pre-Deployment.md)
    * Please refer to the documentation in the point above for the updated list of parameters


- EO Pre Deployment
    * This stage breaks off into a different pipeline execution, the EO-Pre-Deployment pipeline
    * The Spinnaker flow covers the pre steps from the EO Deployment document.
    * More information about this pipeline can be found at [EO-Pre-Deployment.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/flows/EO-Pre-Deployment.md)
    * Please refer to the documentation in the point above for the updated list of parameters


- Install using Helmfile
    * Deploys the EIC Helmfile onto the cluster
    * Uses the helmfile-deploy Jenkins job [helmfileDeploy.jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/helmfileDeploy.Jenkinsfile)
    * More information about this job can be found at [helmfile-deploy.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/helmfile-deploy.md)
    * Please refer to the job and documentation in the points above for the updated list of parameters


- Unreserve Namespace
    * Used to free up the environment that was used as part of the flow
    * Uses the unreserveResource Jenkins job [unreserveResource.jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/files/unreserveResource.Jenkinsfile)
    * More information about this job can be found at [unreserveResource.md](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/unreserveResource.md)
    * Please refer to the job and documentation in the points above for the updated list of parameters


## Parameters Overview
The following is a list of parameters that are used within the flow.

| Parameter                       | Description                                                                                               | Default                                                               |
|---------------------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| CHART_NAME                      | Name of the Application chart to be included in the helmfile                                              | eric-oss-common-base                                                  |
| CHART_REPO                      | Repository of the Application chart to be included in the helmfile                                        | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm  |
| CHART_VERSION                   | Version of the Application chart to be included in the helmfile                                           | None                                                                  |
| HELMFILE_CHART_NAME             | Name of the Helmfile for checking CRDs                                                                    | eric-eiae-helmfile                                                    |
| HELMFILE_CHART_REPO             | Repository of the Helmfile for checking CRDs                                                              | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm/ |
| HELMFILE_CHART_VERSION          | Version of the Helmfile for checking CRDs                                                                 | None                                                                  |
| GERRIT_REFSPEC                  | Gerrit Refspec used to build the Application Chart snapshot                                               | None                                                                  |
| FUNCTIONAL_USER_SECRET          | Functional user for logging into armdocker                                                                | ciloopman-user-creds                                                   |
| ENV_LABEL                       | The environment label attached to the lockable resource                                                   | ticketmaster                                                          |
| SLAVE_LABEL                     | Label to choose which Jenkins slave to execute Jenkinsfiles against                                       | evo_docker_engine_gic_IDUN                                            |
| GERRIT_BRANCH                   | Gerrit Branch for the change to be pushed                                                                 | None                                                                  |
| CI_GERRIT_REFSPEC               | Refspec used to fetch the Jenkins job                                                                     | refs/heads/master                                                     |
| WAIT_SUBMITTABLE_BEFORE_PUBLISH | A boolean value that is used to determine whether a patchset is marked as verified before being submitted | true                                                                  |
| HELM_TIMEOUT                    | The time in seconds to wait for deployment manager to execute the install before timing out               | 3600                                                                  |
| WAIT_TIME                       | The time limit to wait for the environment to become available. Will fail if the time is exceeded         | 120                                                                   |
| ENV_DETAILS_DIR                 | The directory in the repo (in this job, the submodule eo-integration-ci) to find the environment details  | eo-integration-ci/honeypots/pooling/environments                      |
| PATH_TO_SITE_VALUES_FILE        | The path to the site values file necessary for the deployment                                             | site-values/idun/ci/template/site-values-latest.yaml                  |
| TAGS                            | Tags used to specify the applications to be switched on for the deployment                                | so pf uds adc th dmm eas appmgr ch ta os pmh                          |
| HELMFILE_GERRIT_REFSPEC         | Gerrit REF Spec is used by Inca to pull down a code review to build a new Helmfile                        |                                                                       |
| HELMFILE_TYPE                   | The type of Helmfile to deploy, EIC or EO                                                                 | EIC                                                                   |

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
