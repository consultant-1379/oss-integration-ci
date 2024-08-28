# Create Base Platform Version entry within Baseline Tool Flow.

[TOC]

## Introduction
This flow is used in the creation of a new entry in the Baseline Tool (BLT) created by Hummingbirds, with details of the
newly created Base Baseline version. The BLT is a Dashboard that displays the version of the file created, all the
versions of the applications within the file, what has changed within that version of the file, the JIRA details
associated to the change.

An example of the dashboard can be seen here,
[Baseline Tool (BLT)](https://blt.ews.gic.ericsson.se/#/)


## Stage Overview

This is an overview of the flow

- Evaluate Parent Execution Variables
  - This is a built-in Spinnaker flow that sets parameters to global variables for later use in the flow.

- Create Baseline Tool Entry
  - This is an in built spinnaker flow for executing webhooks.
  - The stage calls the rest API to BLT
  - It creates the new entry by sending in details like
    - New File name to create
    - Version of the New File
    - Details of the content changed
    - Jira Ticket number
    - Jira Ticket header
  - With this info, a new entry is added to the BLT dashboard.

## Parameters Overview
The following is a list of parameters that are used within the file.

| Parameter          | Description                                                                                           | Default |
|--------------------|-------------------------------------------------------------------------------------------------------|---------|
| Helmfile Name      | Name of the Helmfile to add. E.g.: base-platform-baseline                                             |         |
| Helmfile Version   | Version of the Helmfile to add E.g.: 1.0.0+66                                                         |         |
| Helmfile Repo      | Helmfile Repo E.g.: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm              |         |
| Helm Chart Name    | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg |         |
| Helm Chart Version | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57                          |         |
| Commit Message     | Git message from the review under test                                                                |         |
| Gerrit Review URL  | URL to the gerrit review that created the update                                                      |         |

### Pipeline Maintenance
These flows are stored in a central repository for source-controlled Spinnaker pipelines.
The flows are stored in the following repo: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory: cicd_pipelines_parameters_and_templates/dg_base/pipeline_template/create-base-platform-baseline-tool-entry.json.

Any changes made to the flow should be updated within this repo and sent to the Ticketmaster team for review.

See the following document for more details on the use and rollout of updated flows: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

### Resources

The following is a link to the spinnaker flow
- [Create Base Platform Baseline Tool Entry](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Create-Base-Platform-Baseline-Tool-entry)

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
