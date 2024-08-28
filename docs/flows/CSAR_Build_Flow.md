# CSAR Build Spinnaker Flow.

[TOC]

## Introduction

This spinnaker flow can be used to build the CSAR associated to a project, EO or IDUN.
These steps are
- Get Latest Helmfile
    * Uses the Chart details entered to get the latest helmfile from the specified repo
- Get App Version from HelmFile
    * Downloads the helmfile from the repo
    * Performs a "helm build" on the downloaded helmfile
    * "Helm build" details is used to generate a file that specifies what release(s) from the
    helmfile will be added to the CSAR's
- Build CSAR stages
    * Each CSAR to be built has a seperate stage in the flow.
- Build Helmfile CSAR
    * Builds a CSAR of the Helmfile if the Helmfile name is found within the "Get App Version From Helmfile" stage
- Generate CSAR Properties
    * Used to gather the details of the CSAR's that have been built.

> **Note** This spinnaker flow should be used for EO & IDUN CSAR building only. Each project should have their own upstream
flow that calls this main flow.

## Stage Overview

This is an overview of the csar build stages, the parameters used for each section:

- Get Latest Helmfile
    * This job is used as part of multiple spinnaker flows.
    * It is used to fetch the latest version of a given helm chart or helmfile.
    * For more info on the Jenkins File see description page, [getLatestChartOrHelmfile.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/getLatestChartOrHelmfile.md)

- Get App Version from HelmFile
    * This is used to build up a properties file that will list all the CSAR and their associated chart to be
    included in the CSAR.
    * For more info on the Jenkins File see description page, [getReleaseInfoFromHelmfile.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/getReleaseInfoFromHelmfile.md)

- Build CSAR stages
    * This point in the spinnaker flow is broken into multiple parallel stages.
    * Each CSAR to be built has it's own stage.
    * Details from the properties file generated in the stage, "Get App Version from HelmFile" is used to pass
    details to each of the stages.
    * The details passed is the chart(s) details to be included in the CSAR.
    * The main release in the helmfile with the csar label, it's details are used for the CSAR name and version.
        * Example

            Below is a snippet of the CNCS release from a helmfile, from this we can see that the csar label is eric-cloud-native-base.
            This will indicated that this is the main CSAR, so the name and version from the snippet below
            will be used for the CSAR, so the CSAR name will be eric-cloud-native-base-55.1.0.csar
            ```
          - name: eric-cloud-native-base
            namespace: {{ .Values | get "helmfile.app.namespace" "eric-app-ns" }}
            chart: {{ .Values | get "repository" "eric-cloud-native-base" }}/eric-cloud-native-base
            needs:
              - eric-cncs-oss-pre-config
            version: 55.1.0
            installed: true
            labels:
              csar: eric-cloud-native-base
            ```
    * For more info on the Jenkins File see description page, [helmCsarBuilder.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Helm_CSAR_Builder.md)

- Build Helmfile CSAR
  * Builds a CSAR of the Helmfile if the Helmfile name is found within the "Get App Version From Helmfile" stage
  * For more info on the Jenkins File see description page, [helmfileCsarBuilder.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Helmfile_CSAR_Builder.md)

- Generate CSAR Properties
    * Used to gather the details of the CSAR's that have been built.
    * Displays all details back in the artifact.properties file which is attached to the Jenkins file.
    * For more info on the Jenkins File see description page, [csarProperties.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/getCsarProperties.md)

## Parameters Overview
The following is a list of parameters that are used within the file.

| Parameter                 | Description                                                                 | Default                                                              |
|---------------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------|
| INT_CHART_VERSION         | The version of helmfile to get the CSAR dewtails from.                      | 0.0.0                                                                |
| INT_CHART_NAME            | Helmfile Name to get the CSAR details from.                                 | eric-eiae-helmfile                                                   |
| INT_CHART_REPO            | Helmfile Repo to pull the Helmfile from                                     | https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm |
| PATH_TO_HELMFILE          | Full path to the helmfile.yaml once the helfile has been extracted          | eric-eiae-helmfile/helmfile.yaml                                     |
| STATE_VALUES_FILE         | Values file used to turn on what need to be build                           | eric-eiae-helmfile/build-environment/tags_true.yaml                  |
| SLAVE_LABEL               | Jenkins Slave label to execute against                                      | evo_docker_engine_athlone                                            |

### Pipeline Maintenance
These flows are stored in a central repository for source-controlled Spinnaker pipelines.
The flows are stored in the following repo: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory: cicd_pipelines_parameters_and_templates/dg_base/pipeline_template/csar_builder_dg_base.json/.

Any changes made to the flow should be updated within this repo and sent to the Ticketmaster team for review.

See the following document for more details on the use and rollout of updated flows: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

See the following document for more details on the rollout of updated flows for the CSAR Spinnaker Flow: [CSAR Spinnaker Pipeline Updates](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=DGBase&title=CSAR+spinnaker+pipeline+updates).

### Resources

The following is a link to the spinnaker flow
- [OSS CSAR Building Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=oss-csar-build-flow)

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
