# OSS Helmfile Deploy Jenkins File using the Deployment Inventory Tool (DIT)

## Introduction

This Jenkins file is used to execute the OSS Helm File Deploy job. This job will take in a large set of input parameters
(described below) and use these parameters to deploy a helm file package into a cluster.

The job is used to automate the initial install and upgrade steps for the OSS products. This includes using the deployment
manager to create an initial workdir, create all the secrets needed to run the full deployment and collect all the logs
generated as part of the deployment or upgrade.

To use this file the environment details need to be stored within the DIT Tool, see [here](DIT_Deployment_Generation.md)
for details.

## Overview

Currently, when the file is executed, it will

- Pulls down the helmfile version given.
- Pulls down a template site values file and updates it with the appropriate environment parameters.
- Ensures the appropriate CSARs are available for the deployment.
> ***Note:*** Either Full CSARs or Mini CSARs can be deployed
> - "DOWNLOAD_CSARS" is set to false,
>   - Pulls down the individual application helm chart and builds mini CSAR.
>   - Mini CSARs just include the helm chart, no images are included, images will be pulled down from the global docker
>   registry during the deployment phase.
> - "DOWNLOAD_CSARS" is set to true,
>   - It pulls down the officially released full CSARs. If a CSAR is not found the deployment will exit.
- Using the deployment manager, the job will create the appropriate directory structure, load in the certificates needed,
load in the kube config file in order to access the target cluster and start the install/upgrade
based off the inputted parameters.
- If the deployment fails it will gather the environment logs from the failed system and attach them to the Jenkins job
as an archived file for analysis.

## Resources

- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Helmfile-Deploy-Using-dit/)

## Prerequisite

To be able to use this Jenkins job the following needs to be fulfilled

- The environment certificates have been stored in OST in the environment certificates bucket, see
[here](OST_Deployment_Certificates_Bucket_Generation.md) for details
- The environment associated files, (kube_config.yaml) have been stored in OST in the files bucket for the
environment, see [here](OST_Deployment_Files_Bucket_Generation.md) for details.
- The environment details need to be stored within the DIT Tool, see [here](DIT_Deployment_Generation.md) for details.
- The appropriate credentials are added to the Jenkins credentials area, see [here](Credentials_Storage.md) for details.
- **Optional**: If deploying real CSARs the local deployment environment docker credentials need to be added to the
Jenkins credentials.
This is needed to pull the application images during the deployment.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/deployment/helmfileDeployUsingDIT.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following job is used within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Helmfile-Deploy-Using-dit/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                               | Description                                                                                                                                                                                                                                                                                                                                                                                                                    | Defaults                                                                         |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| FLOW_AREA                               | This parameter refers to the lifecycle stage of EIAP. Eg. eiapaas, release, productstaging, appstaging, etc. (aaS Use ONLY)                                                                                                                                                                                                                                                                                                    | default                                                                          |
| INT_CHART_VERSION                       | Version of the helmfile to install, e.g. 1.1.1                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                  |
| INT_CHART_NAME                          | Helmfile Name, i.e. eric-eiae-helmfile                                                                                                                                                                                                                                                                                                                                                                                         |                                                                                  |
| INT_CHART_REPO                          | Repo URL to fetch the helmfile file from                                                                                                                                                                                                                                                                                                                                                                                       | https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm                   |
| DEPLOYMENT_TYPE                         | Deployment Type, set "install" or "upgrade"                                                                                                                                                                                                                                                                                                                                                                                    | install                                                                          |
| DEPLOYMENT_NAME                         | This is the name of the document within the DIT tool that is storing the deployment information                                                                                                                                                                                                                                                                                                                                |                                                                                  |
| TAGS                                    | List of tags for applications that have to be deployed (e.g: so adc pf). Enter "None" into this field to leave all tags as false, only base will be deployed.                                                                                                                                                                                                                                                                  |                                                                                  |
| SITE_VALUES_FILE_NAME                   | Name of the site values template to use that is stored in object store, including the file extension                                                                                                                                                                                                                                                                                                                           | site-values-latest.yaml                                                          |
| SITE_VALUE_FILE_BUCKET_NAME             | Name of the bucket that is storing the site values that is stored in object store. Defaults to eic_site_values_template. The following are currently available [eic_site_values_template](https://atvost.athtem.eei.ericsson.se/buckets/view/639317bdcbaaf33a4be728ca) or [eo_site_values_template](https://atvost.athtem.eei.ericsson.se/buckets/view/649c3d0ab413e6b17865e57b)                                               | eic_site_values_template                                                         |
| SITE_VALUES_OVERRIDE_FILE_NAME          | Name of the overwrite site values to use that is stored in object store, including the file extension. Content will override the content for the site values set in the SITE_VALUES_FILE_NAME parameter.                                                                                                                                                                                                                       |                                                                                  |
| SITE_VALUE_OVERRIDE_BUCKET_NAME         | Name of the bucket that is storing the overwrite site values that is stored in object store. Defaults to eic_site_values_override. The following are currently available [eic_site_values_override](https://atvost.athtem.eei.ericsson.se/buckets/view/639318aecbaaf30215e728ce) or [eo_site_values_override](https://atvost.athtem.eei.ericsson.se/buckets/view/649c3da0b413e63f0e65e57f)                                     | eic_site_values_override                                                         |
| IDUN_USER_SECRET                        | Jenkins Credentials secret for default aaS user and password. (aaS Use ONLY). This would be saved in the Jenkins credentials area the same as storing "User Credentials", see [credential storage](Credentials_Storage.md) for details                                                                                                                                                                                         | idun_credentials                                                                 |
| PATH_TO_AWS_FILES                       | Path within the Repo to the location of the Idun aaS AWS credentials and config (aaS Use ONLY)                                                                                                                                                                                                                                                                                                                                 | NONE                                                                             |
| AWS_ECR_TOKEN                           | AWS ECR token for aws public environments for Idun aaS (aaS Use ONLY)                                                                                                                                                                                                                                                                                                                                                          | NONE                                                                             |
| DOWNLOAD_CSARS                          | When set to true the script will try to download the officially released CSARs relation to the version of the applications within the helmfile being deployed. <br/><br/>If set to true, ensure the DOCKER_REGISTRY & DOCKER_REGISTRY_CREDENTIALS parameters are set appropriately                                                                                                                                             | false                                                                            |
| DOCKER_REGISTRY                         | Set this to the docker registry to execute the deployment from. Used when deploying from officially released CSARs <br /><br/> If the parameter "DOWNLOAD_CSARS" is set to true, this parameter should be set to clusters local registry, which needs to be a real FQDN with an entry in DNS.                                                                                                                                  | armdocker.rnd.ericsson.se                                                        |
| DOCKER_REGISTRY_CREDENTIALS             | Jenkins Credentials secret, for the environment docker registry. Not needed if deploying from armdocker.rnd.ericsson.se, <br /><br/> If the paramater "DOWNLOAD_CSARS" is set to true, this needs to be set, to the local docker registry Jenkins credentials secret. This would be saved in the Jenkins credentials area the same as storing "User Credentials", see [credential storage](Credentials_Storage.md) for details | None                                                                             |
| ARMDOCKER_USER_SECRET                   | Jenkins Credentials secret, for ARM Docker, see [credential storage](Credentials_Storage.md) for details                                                                                                                                                                                                                                                                                                                       |                                                                                  |
| FUNCTIONAL_USER_SECRET                  | Jenkins Credentials secret, that hold username and password for functional user, see [credential storage](Credentials_Storage.md) for details                                                                                                                                                                                                                                                                                  |                                                                                  |
| FUNCTIONAL_USER_TOKEN                   | Jenkins Credentials secret, token ID for ARM Registry, see [credential storage](Credentials_Storage.md) for details                                                                                                                                                                                                                                                                                                            | NONE                                                                             |
| DDP_AUTO_UPLOAD                         | Set it to "true" when enabling the DDP auto upload and also need to add the DDP instance details into kubernetes config file and the override site values file                                                                                                                                                                                                                                                                 | false                                                                            |
| USE_DM_PREPARE                          | When set to true uses the site values generated from the Deployment manager prepare command for the deployment. <br/> <br/>**Note:** The values within the prepared site values from the Deployment manager, will be overwritten by the values generated in the CI Site values for both initial install and upgrade, extra keys that maybe in the CI site values are not added.                                                | false                                                                            |
| USE_SKIP_IMAGE_PUSH                     | Set to true to use the Deployment Manager parameter "--skip-image-check-push" in case an image push is done in advance. If false will deploy without the "--skip-image-check-push" parameter.                                                                                                                                                                                                                                  | false                                                                            |
| USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES | Set to true to use the Deployment Manager parameter "--skip-upgrade-for-unchanged-releases" to skip helm upgrades for helm releases whose versions and values have not changed. If false will deploy without the "--skip-upgrade-for-unchanged-releases" parameter'.                                                                                                                                                           | false                                                                            |
| USE_CERTM                               | Set to true to use the "--use-certm" tag during the deployment                                                                                                                                                                                                                                                                                                                                                                 | false                                                                            |
| COLLECT_LOGS                            | If set to "true" (by default) - logs will be collected. If false - will not collect logs.                                                                                                                                                                                                                                                                                                                                      | false                                                                            |
| COLLECT_LOGS_WITH_DM                    | If set to "false" (by default) - logs will be collected by ADP logs collection script. If true - with deployment-manager tool.                                                                                                                                                                                                                                                                                                 | false                                                                            |
| HELM_TIMEOUT                            | Time in seconds for the Deployment Manager to wait for the deployment to execute                                                                                                                                                                                                                                                                                                                                               | 1800                                                                             |
| DOCKER_TIMEOUT                          | Time in seconds for the Deployment Manager to wait for the pulling of docker images to be used for deployment                                                                                                                                                                                                                                                                                                                  | 60                                                                               |
| VERBOSITY                               | Verbosity Level for Deployment Manager. Verbosity can be from 0 to 4. Default is 3. Set to 4 if debug needed                                                                                                                                                                                                                                                                                                                   | 3                                                                                |
| TIMEOUT                                 | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                                                                                                                          | 3600                                                                             |
| SUBMODULE_SYNC_TIMEOUT                  | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                                                                                                                  | 60                                                                               |
| SUBMODULE_UPDATE_TIMEOUT                | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                                                                                                                | 300                                                                              |
| SLAVE_LABEL                             | Specify the label for the Jenkins agent where the job should run.                                                                                                                                                                                                                                                                                                                                                              | evo_docker_engine                                                                |
| DEPLOYMENT_MANAGER_DOCKER_IMAGE         | The full image url and tag for the deployment manager to use for the deployment testing. If the tag is set to default, the deployment manager info will be fetched from the dm_version.yaml file if it exists in the helmfile tar file under test.                                                                                                                                                                             | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:default |
| CI_DOCKER_IMAGE                         | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image version. Other option available, latest or a specific version.                                                                                                                                                                            | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default         |
| CI_GERRIT_REFSPEC                       | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                                                                                                                                                                 | refs/heads/master                                                                |

>> **Note** See the following pages for more details on
> - Credential's storage, [README](Credentials_Storage.md)
> - Environment Storage in Deployment Inventory Tool (DIT), [README](DIT_Deployment_Generation.md) for details.

> NOTE
> Prerequisites for using the CSAR Download Functionality:

> - Jenkins Slave needs a connection to the local docker registry in the deployment.
> - Jenkins Slave should have sufficient root storage to hold the CSARs (Total CSAR size X 3.5)

> Why 3.5 times the CSAR size,
> - Download the CSAR's to the Root Disk
> - Extraction of the Images to the Root disk
> - Load the images into Docker for upload to the local docker registry.


#### Output File

An artifact.properties file is generated and attached to the Jenkins execution at the end of the flow assuming the deployment/upgrade was successful.

This artifact.properties file will contain the deployment manager version used for the deployment.

Ex:
```
DEPLOYMENT_MANAGER_VERSION=1.37.0-45
```

Alternatively, if the deployment/upgrade fails then we will get a different set of output files. This logs can be used
for troubleshooting. The list of logs are not guaranteed, as it depends where in the deployment it fails.
- ci-script-executor-logs (directory)
  - This will list all debug logs from the CI Docker image.
- logs (directory)
  - These are the logs that are generated by Deployment manager during its execution phases.
- logs_oss-deploy_<TIMESTAMP>.tgz (file)
  - This is a tar file of all the logs from the kubernetes system itself.
-  site_values_<HELMFILE-VERSION>.yaml (file)
  - This is the site values that was used in the deployment.

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
    * **Script Path:** ci/jenkins/files/deployment/helmfileDeployUsingDIT.Jenkinsfile
> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though on first execution, but this is expected behaviour.


### ENV_CONFIG_FILE

Set ENV_CONFIG_FILE to /dummy/path/to/config/file.conf<br>
Snip of the Contents of that file:
```
...
# Hostnames for the Deployment
EO_VNFM_HOSTNAME=evnfm.hart904.rnd.gic.ericsson.se
EO_SO_HOSTNAME=so.hart904.rnd.gic.ericsson.se
EO_SO_TEST_HOSTNAME_1=auth.server1.hart904.rnd.gic.ericsson.se
EO_SO_TEST_HOSTNAME_2=mtls.server1.hart904.rnd.gic.ericsson.se
EO_PF_HOSTNAME=pf.hart904.rnd.gic.ericsson.see
...
```

Snip of Contents of PATH_TO_SITE_VALUES_OVERRIDE_FILE:
```
eric-eo-so:
  eric-eo-auth-test:
    ingress:
      hostname: EO_SO_TEST_HOSTNAME_1
      tls:
        enabled: true
      mtls:
        hostname: EO_SO_TEST_HOSTNAME_2
        enabled: true
```

Output in the site values file for deployment:
```
eric-eo-so:
  eric-eo-auth-test:
    ingress:
      hostname: auth.server1.hart904.rnd.gic.ericsson.se
      tls:
        enabled: true
      mtls:
        hostname: mtls.server1.hart904.rnd.gic.ericsson.se
        enabled: true
```

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

