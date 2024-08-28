# Base Platform Baseline Generation Flow.

[TOC]

## Introduction
This flow is used in the generation of the Base Platform Baseline version file.
This version file is stored in an internal repo, in a helmfile format. See the following repo,
[Base Platform Baseline File Repo](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-base-baseline/+/refs/heads/master)

This file is used to hold all the Base platform application versions that make up a specific baseline.
Each baseline file generated has a unique version, this version of the file can be passed to the PSO areas.
Using this version, the Baseline information for the base applications which have been tested in Base platform flows can be
retrieved.

## Stage Overview

This is an overview of the flow, there are two main flows through the flow, the general flow where items are added to
the master branch or if an EP(Emergency Package) is required, this flow can also generate that branch version.
For more on the EP generation please see, [Base-Platform-Baseline-EP-Generation](Base-Platform-Baseline-EP-Generation.md)

Master Branch Push
  - Build Base Platform Baseline:
    - Pulls down the Base Platform repository and checks out master
    - Takes the new base application version(s) and adds it to helmfile
    - Packages up the helmfile and pushes to the snapshot or drop repo, depending on the "GERRIT_PREPARE_OR_PUBLISH"
    parameter used.
    - Will push the new version to repo and tag the repo if the "GERRIT_PREPARE_OR_PUBLISH" parameter is set to "publish".
    - See [Base_Platform_Baseline_Fetch_Build_Upload](../files/Base_Platform_Baseline_Fetch_Build_Upload.md) for
    further details on the job
  - Evaluate Variables Base Platform Variables
    - Used to set values to a unique value so can be used further down the flow

EP Branch Push
  - Set New Baseline
    - This is used to set the content for a new base.
    - It takes the version of the Base Platform version file to build on top of.
    - Pulls the content of the version file and swaps the new application chart information for the old.
    - See [Set_Or_Get_Base_Platform_Baseline_App_Versions](../files/Set_Or_Get_Base_Platform_Baseline_App_Versions.md) for
    further details on the job
  - Build EP Base Platform Baseline:
    - Pulls down the Base Platform repository and checks out the EP Branch (Pre created)
    - Takes the new Base Application version and adds it to the helmfile.
    - Packages up the helmfile and pushes to the snapshot or drop repo depending on the "GERRIT_PREPARE_OR_PUBLISH" parameter.
    - Will push the new version to repo and tag the repo if the "GERRIT_PREPARE_OR_PUBLISH" parameter is set to "publish".
    - See [Base_Platform_Baseline_Fetch_Build_Upload](../files/Base_Platform_Baseline_Fetch_Build_Upload.md) for
    further details on the job
  - Evaluate Variables INCA Variables
    - Used to set values to a unique value so can be used further down the flow

Common Stages Between Master and Branch Push
- Check Preconditions
  - Ensure that the two branches previous to this stage completes successfully or were skipped appropriately.

- Get Base Platform Baseline Details
  - Using the version of the Base Platform just created in the previous stages, it pulls all the info from the helmfile
    - This info then can be used in other stages/flows
    - See [Set_Or_Get_Base_Platform_Baseline_App_Versions](../files/Set_Or_Get_Base_Platform_Baseline_App_Versions.md) for
  further details on the job

- Add Base Platform Baseline Entry
  - This is a pipeline flow in itself. It is used to populate the Baseline Tool dashboard created by Hummingbirds
  - It populates the dashboard with the name of the file, file version, content of the file and the new content added to the file.
  - This can be used to compare one version to another to see what has changed.
  - See the following flow for further details [Create-Base-Platfrom-Baseline-Tool-entry](Create-Base-Platform-Baseline-Tool-Entry.md)

## Parameters Overview
The following is a list of parameters that are used within the file.

| Parameter                                    | Description                                                                                                                                                                                         | Default           |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| Helm Chart Name                              | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg                                                                                               |                   |
| Helm Chart Version                           | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57                                                                                                                        |                   |
| Helm Chart Repo                              | Comma-separated dependency helm chart repo list. E.g.: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm   |                   |
| Build Type                                   | prepare :: Prepare Helmfile and uploads to the snapshot/internal repo. publish :: Checks in the updates to git and upload to the drop repo                                                          | prepare           |
| Jenkins Node to build from                   | The Jenkins agents the Jenkins jobs should be executed against                                                                                                                                      | evo_docker_engine |
| Version Check Downgrade                      | Default is 'false', if set to true, version is allowed to step backwards one step only (e.g. 7.1.0-1 -> 7.0.0-1). If set to false, any version step backwards is allowed (E.g. 7.1.0-1 -> 5.1.3-7). | false             |
| Allow Downgrade of Dependency                | Default is 'false', if set to true, downgrade of dependency is allowed.                                                                                                                             | false             |
| Version Step Stratagy                        | Possible values: MAJOR, MINOR, PATCH. Step the version in metadata.yaml when dependency change received. Default is PATCH.                                                                          | MINOR             |
| EP Branch To Build the Helmfile From         | This is only used when building EP releases for Base. Used to specify what branch to build the baseline on for EP                                                                                   | master            |
| Base Platform Baseline Version to build from | This is only used when building EP releases for Base. Used to specify what released version of the baseline should be used for EP build.                                                            | latest            |

### Pipeline Maintenance
These flows are stored in a central repository for source-controlled Spinnaker pipelines.
The flows are stored in the following repo: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory: cicd_pipelines_parameters_and_templates/dg_base/pipeline_template/base-platform-baseline-generation.json.

Any changes made to the flow should be updated within this repo and sent to the Ticketmaster team for review.

See the following document for more details on the use and rollout of updated flows: [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

### Resources

The following is a link to the spinnaker flow
- [Base Platform Baseline Generation](https://spinnaker.rnd.gic.ericsson.se/#/applications/common-cicd/executions?pipeline=Base-Platform-Baseline-Generation)

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

