# OSS Integration CI

[TOC]

## Introduction
This repo contains the OSS Common Service for CI, from script to site value templates.


### Repo Structure
The main parts of the repo are the ci/jenkins/files/, which are used to create the Jenkins jobs, the
site-values/ files which holds the site values templates to execute the deployment and the
ci/jenkins/scripts/python-ci-scripts docker image. This image is used within the Jenkins file to execute different
commands from specific kubernetes commands to site values management.

## Prerequisites
To use any of these Jenkins files, the following are requirements.
- Jenkins agent(s) should have
  - Git version 2.25 or higher
  - Docker version 20.10 or higher
- Teams responsible for a flow should have their own Functional user.
- Users should have access to a Jenkins server to be able to
  - Create jobs
  - Generate Jenkins Credentials
  - Ability to execute jobs.
  - Interact and add Lockable resource (Optional)
- A number of the Jenkins files need certain credentials created as secrets within the Jenkins credentials storage area.
See [here](docs/files/Credentials_Storage.md) for more info on the credential's creation.
- To interact with a kubernetes environment, the environment info should be stored in the environment tools,
  - The environment certificates have been stored in OST in the environment certificates bucket, see
  [here](docs/files/OST_Deployment_Certificates_Bucket_Generation.md) for details
  - The environment associated files, (kube_config.yaml) have been stored in OST in the files bucket for the
  environment, see [here](docs/files/OST_Deployment_Files_Bucket_Generation.md) for details.
  - The environment details need to be stored within the DIT Tool, see [here](docs/files/DIT_Deployment_Generation.md) for details.
  - If the deployment needs an override file, include the file in the appropriate override bucket,
  [eic_site_values_override](https://atvost.athtem.eei.ericsson.se/buckets/view/639318aecbaaf30215e728ce) or
  [eo_site_values_override](https://atvost.athtem.eei.ericsson.se/buckets/view/649c3da0b413e63f0e65e57f)
  > ***Note:*** The functional user that is being used in the flows should be added to the files in OST to ensure it has
access to fetch the data

## Available Jenkins File
#### Chart Management

| File                                        | Description                                                                                                                            | README                                                |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| OSS-Integration-Common-PCR-Test.Jenkinsfile | Used to build a Dev Chart using a dependency cache                                                                                     | [README](docs/files/Dev_Chart_Creation.md)            |
| fetchBuildUploadUsingInca.Jenkinsfile       | This file is used to generate either a chart or helmfile which can be used in the different testing phases using the ADP INCA enabler. | [README](docs/files/Fetch_Build_Upload_Using_Inca.md) |
| packageChartUsingCiHelm.Jenkinsfile         | This file is used to generate a development/snapshot of helm chart which can be used for testing purposes.                             | [README](docs/files/Dev_Chart_Creation.md)            |

#### Pre Code Review Related Jenkins file
| File                                        | Description                               | README                                  |
|---------------------------------------------|-------------------------------------------|-----------------------------------------|
| OSS-Integration-Common-PCR-Test.Jenkinsfile | Used to execute PCR against a given chart | [README](docs/files/Common_App_Test.md) |

#### Deployment Related Jenkins files
| File                                          | Description                                                                                                                       | README                                                        |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| purge.Jenkinsfile                             | Used to completely clean down the namespace and all its associated resources depending on the options set.                        | [README](docs/files/Purge.md)                                 |
| create-namespace.Jenkinsfile                  | Used to create a namespace on a kubernetes cluster                                                                                | [README](docs/files/Create_Namespace.md)                      |
| create-namespace-secret.Jenkinsfile           | OSS Create a new namespace secret within the given cluster using the docker secret as the credentials                             | [README](docs/files/Create_Namespace_Secret.md)               |
| enm-container-vnfm-connectivity.Jenkinsfile   | Used to create the secret that is required for the Container VNFM and the ENM connectivity.                                       | [README](docs/files/ENM_Container_VNFM_Connectivity.md)       |
| enm-vm-vnfm-connectivity.Jenkinsfile          | Used to create the secret that is required for the VM VNFM and the ENM connectivity.                                              | [README](docs/files/ENM_VM_VNFM_Connectivity.md)              |
| checkHelmfileDeployment.Jenkinsfile           | Used to ensure the deployment is in a good state before executing any tests on the system                                         | [README](docs/files/Check_Helmfile_Deployment.md)             |
| gatherEnvDetails.Jenkinsfile                  | Used to gather all the environment details for a given system inputted                                                            | [README](docs/files/Gather_Environment_Details.md)            |
| getKubernetesLogs.Jenkinsfile                 | Used to gather the logs for a specific environment                                                                                | [README](docs/files/Get_Kubernetes_Logs.md)                   |
| helmfileDeploy.Jenkinsfile                    | Used to execute the deployment using a given helmfile                                                                             | [README](docs/files/Helmfile_Deploy.md)                       |
| helmfileDeployUsingDIT.Jenkinsfile            | Used to execute the deployment using a given helmfile and fetch the environment details using the Deployment Inventory Tool (DIT) | [README](docs/files/Helmfile_Deploy_Using_DIT.md)             |
| quarantineResource.Jenkinsfile                | Used to quarantine a resource from the lockable resources within jenkins                                                          | [README](docs/files/Quarantine_Resource.md)                   |
| reserveResource.Jenkinsfile                   | Used to reserve a resource from the lockable resources within jenkins                                                             | [README](docs/files/Reserve_Resource.md)                      |
| unreserveResource.Jenkinsfile                 | Used to unreserve a resource from the lockable resources within jenkins                                                           | [README](docs/files/Unreserve_Resource.md)                    |
| evnfm-pre-deployment.Jenkinsfile              | Used to execute the EVNFM Specific pre deployment steps                                                                           | [README](docs/files/EVNFM_Pre-Deployment.md)                  |
| am-specific-role-binding.Jenkinsfile          | Used to execute the AM Specific cluster role binding creation                                                                     | [README](docs/files/AM-Specific_Role_Binding.md)              |
| custom-cluster-role.Jenkinsfile               | Used to create a custom cluster role.                                                                                             | [README](docs/files/Custom_Cluster_Role.md)                   |
| database-pg-secret.Jenkinsfile                | Used to create the Postgres Database secret.                                                                                      | [README](docs/files/Database-PG_secret.md)                    |
| eric-sec-access-mgmt-creds.Jenkinsfile        | Used to create the generic secret called eric-sec-access-mgmt-creds for the IAM admin user.                                       | [README](docs/files/Eric-Sec-Access-Mgmt-Creds_Secret.md)     |
| healthCheckUsingDeploymentManager.Jenkinsfile | Used to execute a health check of a deployment using Deployment Manager Health Check functionality                                | [README](docs/files/Health_Check_Using_Deployment_Manager.md) |


#### CSAR Related Jenkins file
| File                            | Description                                                                                                            | README                                        |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| helmCsarBuilder.Jenkinsfile     | Used to build a Helm CSAR for a given Helm Application using the am package manager                                    | [README](docs/files/Helm_CSAR_Builder.md)     |
| helmfileCsarBuilder.Jenkinsfile | Used to build a Helmfile CSAR for a given Helmfile using the am package manager                                        | [README](docs/files/Helmfile_CSAR_Builder.md) |
| miniCsarBuilder.Jenkinsfile     | Used to build the mini CSARs for all the charts that are currently in the helmfile version.                            | [README](docs/files/Mini_CSAR_Builder.md)     |
| checkCsars.Jenkinsfile          | Used to check if the Csars within a specified Helmfile exist within the Csar Repo                                      | [README](docs/files/Check_CSARs.md)           |
| csarProperties.Jenkinsfile      | Part of the CSAR builder flow to generate all the CSAR links according to the helmfile used to kick off the csar build | [README](docs/files/Get_CSAR_Properties.md)   |

#### Base Platform Baseline Management (Internal Use Only)

| File                                              | Description                                                                                                                                                                            | README                                                                 |
|---------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| setGetBasePlatformBaselineAppVersions.Jenkinsfile | Used to either return the baseline from a given Helmfile or to set a new baseline by taking the given chart details and swapping those details from the helmfile App details returned. | [README](docs/files/Set_Or_Get_Base_Platform_Baseline_App_Versions.md) |
| basePlatformBaselineManagement.Jenkinsfile        | Used to generate a helmfile which can be used to store the DG Base Baseline. It can be used to generate either a snapshot of the artifact or a released version of the artifact.       | [README](docs/files/Base_Platform_Baseline_Fetch_Build_Upload.md)      |

#### Miscellaneous Jenkins file
| File                                            | Description                                                                                                                                                           | README                                                        |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| calculateAppVersionsFromHelmfile.Jenkinsfile    | Used to get all the Application names and version included in a given helmfile                                                                                        | [README](docs/files/Calculate_App_Versions_From_Helmfile.md)  |
| checkEricProductInfoInformation.Jenkinsfile     | Can be used by Application Team Members in order to check if the content being added to the eric-product-info.yaml file is able to be pulled down by the CSAR Builder | [README](docs/files/Check_Eric_Product_Info_Information.md)   |
| gerritNotification.Jenkinsfile                  | Part of the Submit flows to send info back to the gerrit review on how the flow is executing                                                                          | [README](docs/files/Gerrit_Notification.md)                   |
| getLatestChartOrHelmfile.Jenkinsfile            | Used to get the latest helmfile version from a give arm repository                                                                                                    | [README](docs/files/Get_Latest_Chart_Or_Helmfile.md)          |
| checkAppForOfficialDelivery.Jenkinsfile         | Used to check the input chart if it is allowed to be officially released or not                                                                                       | [README](docs/files/Check_App_For_Official_Delivery.md)       |
| getReleaseInfoFromHelmfile.Jenkinsfile          | Used to gather the release info from a given Helmfile.                                                                                                                | [README](docs/files/Get_Release_Info_From_Helmfile.md)        |
| Get-Microservice-Info-From-Helmfile.Jenkinsfile | Used to gather the microservice details present inside the product helmfiles.                                                                                         | [README](docs/files/Get_Microservice_Info_From_Helmfile.md)   |
| checkForCrds.jenkinsfile                        | Used to get CRD tar file info from an application chart                                                                                                               | [README](docs/files/Check_For_CRDs.md)                        |
| cncsOptionalityCheck.Jenkinsfile                | Used to assess whether all the services contained within the CNCS Chart.yaml file are contained within the optionality.yaml file of the helmfile.                     | [README](docs/files/CNCS_Optionality_Checker.md)              |
| updateVersionInProductHelmfile.jenkinsfile      | Used to update the Deployment manager (DM) version in the specified Product Helmfile.                                                                                 | [README](docs/files/Update_DM_Version_In_Product_Helmfile.md) |
| compareLatestVersionsInHelmfile.Jenkinsfile     | Used to compare the current versions of applications in a Helmfile to the latest versions in the relevant repos                                                       | [README](docs/files/Compare_Latest_Versions_In_Helmfile.md)   |

## Available Spinnaker Flow
| File                                                                                                                                                                                           | Description                                                                                                                                                                                                             | README                                                            |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| [EO Pre Deployment Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=EO-Pre-Deployment)                           | This spinnaker flow can be used to execute the EO pre deployment steps.                                                                                                                                                 | [README](docs/flows/EO_Pre-Deployment.md)                         |
| [IDUN Pre Deployment Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=IDUN-Pre-Deployment)                       | This spinnaker flow can be used to execute the IDUN pre deployment steps.                                                                                                                                               | [README](docs/flows/IDUN_Pre-Deployment.md)                       |
| [OSS CSAR Build Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=oss-csar-build-flow)                            | This spinnaker flow can be used to execute the OSS CSAR Build flow.                                                                                                                                                     | [README](docs/flows/CSAR_Build_Flow.md)                           |
| [Ticketmaster Internal CI Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/ticketmaster-e2e-cicd/applications/ticketmaster-cicd/executions)                                              | This spinnaker flow is an internal flow used by the Ticketmaster team to execute tests against the Jenkins file prior to release <br>The start of the flow is the pipeline with "ci-pipeline-release-main" in its name. | [README](docs/flows/Internal_CI_Test_Flow.md)                     |
| [Base Platform Baseline Generation](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Base-Platform-Baseline-Generation)                                    | This spinnaker flow is used in the generation of the Base Platform Baseline version file.                                                                                                                               | [README](docs/flows/Base-Platform-Baseline-Generation.md)         |
| [Base Platform Baseline EP Generation](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Base-Platform-Baseline-EP-Generation)                              | This spinnaker flow is used in the generation an Emergency correction(EP) of the Base Platform Baseline version file.                                                                                                   | [README](docs/flows/Base-Platform-Baseline-EP-Generation.md)      |
| [Create Base Platform Baseline Tool Entry](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Create-Base-Platform-Baseline-Tool-entry)                      | This spinnaker flow is used in the update the Baseline Tool (BLT) created by Hummingbirds with details of the newly created Baseline version.                                                                           | [README](docs/flows/Create-Base-Platform-Baseline-Tool-Entry.md)  |

## OSS CI Docker Image
More info on the Ticketmaster CI Docker Image, eric-oss-ci-scripts image, can be seen in the following page, [README](docs/eric-oss-ci-scripts/eric-oss-ci-scripts_image.md).

## Deployment Instruction
#### EO Deployment
Please see EO Helmfile Repo for details - [eo-helmfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eo/eo-helmfile/+/refs/heads/master)

#### IDUN Deployment
Please see the IDUN Helmfile Repo for details - [idun-helmfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/refs/heads/master)

## Release Notes

## Community
### Key people of the project
- PO
    - Jimmy Casey (jimmy.a.casey@ericsson.com)
- Guardians (Code reviews, approvals, house rules etc.)
    - Ticketmaster (PDLTICKETM@pdl.internal.ericsson.com)

### Contact
- Send questions via [General Chat](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
- Create new support on Ticketmaster: [Support](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)
### Contributing
We're an inner source project and welcome contributions. See our [Contribution
Guide](docs/Contribution_Guide.md) for more details.
- Join and post on the [Code Review Requests](https://teams.microsoft.com/l/channel/19%3a24a63aa23b484b8092251565822c18f0%40thread.skype/Code%2520Review%2520Requests?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  channel of the Honey Pots team on Microsoft Teams.

## FAQ
Please see [FAQ](docs/FAQ.md)


