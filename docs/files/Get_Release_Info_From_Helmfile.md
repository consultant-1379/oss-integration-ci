# Get Release Info From Helmfile

[TOC]

## Introduction

The job is used to gather the release info from a given Helmfile.


## Overview
Currently, when the file is executed,
- The Jenkins job will take in parameters from the user (All Input Parameters are listed in more detail below).
- Using the parameters it will pull down the Helmfile and extract- It uses inputted state values file and the extracted chart and executes a "helm build". The helm build output a json
of all the build values set from the helmfile.yaml, crd-helmfile.yaml.
- With the CSAR on the top level, it will list the helmfile information from the metadata file.
- This build file is used to generate a number of files which can be used by different spinnaker flows. These generated files are explained below.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/getReleaseInfoFromHelmfile.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following is an example of the Jenkinsfile used in a job within the spinnaker flows.
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/Get-Release-Info-From-Helmfile/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                    | Default                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| INT_CHART_VERSION        | The version of helmfile to download and extract                                                                                                                                                                                                                |                                                                          |
| INT_CHART_NAME           | Helmfile Name to download                                                                                                                                                                                                                                      | eric-eiae-helmfile                                                       |
| INT_CHART_REPO           | Helmfile Repo to download the helmfile from                                                                                                                                                                                                                    | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm     |
| FUNCTIONAL_USER_SECRET   | Jenkins secret ID for ARM Registry Credentials                                                                                                                                                                                                                 | ciloopman-user-creds                                                      |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                          | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                  | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on                                                                                                                                                                                                        | evo_docker_engine                                                        |
| PATH_TO_HELMFILE         | Path to the helmfile                                                                                                                                                                                                                                           | eric-eiae-helmfile/helmfile.yaml                                         |
| STATE_VALUES_FILE        | Path to populated site-values file                                                                                                                                                                                                                             | eric-eiae-helmfile/build-environment/tags_true.yaml                      |
| GET_ALL_IMAGES           | Set a true or false boolean to state whether to gather all release info independent of state values file                                                                                                                                                       | refs/heads/master                                                        |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows. If the version for the image is set to default, the version in VERSION_PREFIX file from the repo is used to fetch the image. Other option available, latest or a specific version.                    | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| GERRIT_REFSPEC           | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

A number of files are generated when the script executes
* helmfile_json_content.json - this is the output of the "helm build" in a json format

    Example:
    ```
    {
    "eric-cloud-native-base": {
        "chart": "eric-cloud-native-base/eric-cloud-native-base",
        "installed": true,
        "labels": {
            "csar": "eric-cloud-native-base"
        },
        "name": "eric-cloud-native-base",
        "namespace": "eric-app-ns",
        "url": "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/",
        "values": [
            {
                "eric-cloud-native-kvdb-rd-operand": {
                    "enabled": false
                },
                "eric-cm-mediator": {
                    "enabled": false
                },
                "eric-cm-mediator-db-pg": {
                    "enabled": false
                },
                "eric-ctrl-bro": {
                    "enabled": true
                },
                "eric-data-coordinator-zk": {
                    "enabled": true
                },
                "eric-data-distributed-coordinator-ed": {
                    "enabled": false
                },
                "eric-data-document-database-pg": {
                    "enabled": false
                },
                "eric-data-key-value-database-rd": {
                    "enabled": false
                },
                "eric-data-message-bus-kf": {
                    "enabled": true
                },
                "eric-data-object-storage-mn": {
                    "enabled": true
                },
                "eric-data-search-engine": {
                    "enabled": true
                },
                "eric-data-search-engine-curator": {
                    "enabled": true
                },
                "eric-dst-agent": {
                    "enabled": false
                },
                "eric-dst-collector": {
                    "enabled": false
                },
                "eric-fh-alarm-handler": {
                    "enabled": false
                },
                "eric-fh-alarm-handler-db-pg": {
                    "enabled": false
                },
                "eric-fh-snmp-alarm-provider": {
                    "enabled": false
                },
                "eric-lm-combined-server": {
                    "enabled": false
                },
                "eric-lm-combined-server-db-pg": {
                    "enabled": false
                },
                "eric-log-shipper": {
                    "enabled": true
                },
                "eric-log-transformer": {
                    "enabled": true
                },
                "eric-odca-diagnostic-data-collector": {
                    "enabled": false
                },
                "eric-pm-server": {
                    "enabled": true
                },
                "eric-sec-access-mgmt": {
                    "enabled": true
                },
                "eric-sec-access-mgmt-db-pg": {
                    "enabled": true
                },
                "eric-sec-certm": {
                    "enabled": false
                },
                "eric-sec-key-management": {
                    "enabled": true
                },
                "eric-sec-sip-tls": {
                    "enabled": true
                },
                "eric-si-application-sys-info-handler": {
                    "enabled": false
                },
                "eric-tm-ingress-controller-cr": {
                    "enabled": true
                }
            },
            "./values-templates/eric-cloud-native-base-site-values.yaml.gotmpl"
        ],
        "version": "55.1.0"
    },
    ```
* releases_and_associated_csar.json - A json list of all the releases from the helmfile.yaml and the crd-helmfile.yaml and
the csar that they are associated to.

    Example:
    ```
    {
    "eric-cloud-native-base": "eric-cloud-native-base",
    "eric-cncs-oss-config": "eric-cncs-oss-config",
    "eric-data-wide-column-database-cd-crd": "eric-cloud-native-base",
    "eric-eo-act-cna": "eric-eo-act-cna",
    "eric-eo-cm": "eric-eo-cm",
    "eric-eo-evnfm": "eric-eo-evnfm",
    "eric-eo-evnfm-vm": "eric-eo-evnfm-vm",
    "eric-eo-so": "eric-eo-so",
    "eric-mesh-controller-crd": "eric-cloud-native-base",
    "eric-oss-common-base": "eric-oss-common-base",
    "eric-oss-config-handling": "eric-oss-config-handling",
    "eric-oss-dmm": "eric-oss-dmm",
    "eric-oss-ericsson-adaptation": "eric-oss-ericsson-adaptation",
    "eric-oss-kf-sz-op-crd": "eric-cloud-native-base",
    "eric-oss-pf": "eric-oss-pf",
    "eric-oss-uds": "eric-oss-uds",
    "eric-sec-sip-tls-crd": "eric-cloud-native-base",
    "eric-tm-ingress-controller-cr-crd": "eric-cloud-native-base",
    "eric-topology-handling": "eric-topology-handling"
    }
    ```
* csar_to_be_built.properties - A list of CSAR's to be built and there versions

    Example:
    ```
    eric-eiae-helmfile_name:2.939.0
    eric-cloud-native-base:56.2.0
    eric-cncs-oss-config:0.0.0-28
    eric-oss-common-base:0.1.0-596
    eric-eo-so:3.5.0-5
    eric-oss-pf:2.7.0-19
    eric-oss-uds:5.1.0-21
    eric-eo-evnfm:2.23.0-633
    eric-eo-evnfm-vm:2.38.0-1
    eric-oss-ericsson-adaptation:0.1.0-562
    eric-oss-dmm:0.0.0-132
    eric-topology-handling:0.0.2-67
    eric-oss-config-handling:0.0.0-81
    eric-eo-cm:1.10.0-107
    eric-eo-act-cna:1.7.0-3
    ```
* csar_build.properties - This is used to pass what chart should be included into each of the CSAR's

    Example:
    ```
    eric-eiae-helmfile_name=eric-eiae-helmfile
    eric-eiae-helmfile_version=2.939.0
    eric-eiae-helmfile_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm
    eric-cloud-native-base_name=eric-cloud-native-base,eric-tm-ingress-controller-cr-crd,eric-mesh-controller-crd,eric-sec-sip-tls-crd,eric-data-wide-column-database-cd-crd,eric-oss-kf-sz-op-crd
    eric-cloud-native-base_version=56.2.0,11.0.0+29,6.0.0+78,4.2.0+32,1.10.0+10,0.27.1-0
    eric-cloud-native-base_url=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm,https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm,https://arm.seli.gic.ericsson.se/artifactory/proj-est-strimzi-drop-helm
    eric-cncs-oss-config_name=eric-cncs-oss-config
    eric-cncs-oss-config_version=0.0.0-28
    eric-cncs-oss-config_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm
    eric-oss-common-base_name=eric-oss-common-base
    eric-oss-common-base_version=0.1.0-596
    eric-oss-common-base_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm
    eric-eo-so_name=eric-eo-so
    eric-eo-so_version=3.5.0-5
    eric-eo-so_url=https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/
    eric-oss-pf_name=eric-oss-pf
    eric-oss-pf_version=2.7.0-19
    eric-oss-pf_url=https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/
    eric-oss-uds_name=eric-oss-uds
    eric-oss-uds_version=5.1.0-21
    eric-oss-uds_url=https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/
    eric-eo-evnfm_name=eric-eo-evnfm
    eric-eo-evnfm_version=2.23.0-633
    eric-eo-evnfm_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eo-evnfm-drop-helm
    eric-eo-evnfm-vm_name=eric-eo-evnfm-vm
    eric-eo-evnfm-vm_version=2.38.0-1
    eric-eo-evnfm-vm_url=https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-vnflcm-helm
    eric-oss-ericsson-adaptation_name=eric-oss-ericsson-adaptation
    eric-oss-ericsson-adaptation_version=0.1.0-562
    eric-oss-ericsson-adaptation_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
    eric-oss-dmm_name=eric-oss-dmm
    eric-oss-dmm_version=0.0.0-132
    eric-oss-dmm_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
    eric-topology-handling_name=eric-topology-handling
    eric-topology-handling_version=0.0.2-67
    eric-topology-handling_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
    eric-oss-config-handling_name=eric-oss-config-handling
    eric-oss-config-handling_version=0.0.0-81
    eric-oss-config-handling_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
    eric-eo-cm_name=eric-eo-cm
    eric-eo-cm_version=1.10.0-107
    eric-eo-cm_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eo-cm-helm
    eric-eo-act-cna_name=eric-eo-act-cna
    eric-eo-act-cna_version=1.7.0-3
    eric-eo-act-cna_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eo-cm-helm
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
    * **Script Path:** ci/jenkins/files/getReleaseInfoFromHelmfile.Jenkinsfile
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
