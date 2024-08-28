# Base Platform Baseline EP Generation Flow.

[TOC]

## Introduction
This flow is used in the generation of an Emergency Package (EP) of the Base Platform Baseline version file.
This will generate a new Baseline file from a previous released version and step the previous version using the PATCH
of the version.

To use this functionality a branch should be created manually at the point in the repo where the EP should
be created from. The branch should be created on the following repo,
[Base Platform Baseline File Repo](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-base-baseline/+/refs/heads/master)
with the following structure, <version to step from>_EP e.g. 0.3.0_EP

When this flow is executed it will generate a new baseline version and deliver to the drop repo.
This baseline version should be delivered manually to the respective PSO flow, subsequent deliveries from base platform
should be blocked in the PSO flow until there is a fix available.

## Stage Overview

This is an overview of the flow,


Generate Baseline:
    * This calls the overall flow [Base-Platform-Baseline-EP-Generation](Base-Platform-Baseline-EP-Generation.md).
    Please see that flow for its functionality

## Parameters Overview
The following is a list of parameters that are used within the file.

| Parameter                                    | Description                                                                                                                                                                                       | Default |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| Chart Name                                   | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg                                                                                             |         |
| CHART_VERSION                                | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57                                                                                                                      |         |
| CHART_REPO                                   | Comma-separated dependency helm chart repo list. E.g.: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm |         |
| Branch to build From                         | Branch to use to create the new Baseline version under                                                                                                                                            | master  |
| Base Platform Baseline Version to build from | The Version to pull the Base versions from                                                                                                                                                        |         |

### Pipeline Maintenance
These flows are stored in a central repository for source-controlled Spinnaker pipelines.
The flows are stored in the following repo: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory: cicd_pipelines_parameters_and_templates/dg_base/pipeline_template/base-platform-baseline-ep-generation.json.

Any changes made to the flow should be updated within this repo and sent to the Ticketmaster team for review.

See the following document for more details on the use and rollout of updated flows: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

### Resources

The following is a link to the spinnaker flow
- [Base Platform Baseline EP Generation](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Base-Platform-Baseline-EP-Generation)

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


