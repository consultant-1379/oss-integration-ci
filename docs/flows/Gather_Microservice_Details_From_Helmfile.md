# Gather Microservice Details From Helmfile.

[TOC]

## Introduction

This spinnaker flow can be used to gather all the microservice details listed in a product helmfile.
These steps are
- Get Latest Helmfile
    * Uses the Chart details entered to get the latest helmfile from the specified repo
- Get Microservice Info From Project helmfile
    * Downloads the helmfile from the repo
    * Performs a "helm build" on the downloaded helmfile
    * "Helm build" details is used to download all the applications from the helmfile.
    * Each application is extracted to get the microservice details

> **Note** This spinnaker flow is used currently for EO, EIAE & EOOM. If other projects are to be added please contact Ticketmaster.

### Resources

The following is a link to the spinnaker flow
- [Get Microservice Info From Helmfile](https://spinnaker.rnd.gic.ericsson.se/#/projects/ticketmaster-e2e-cicd/applications/common-cicd/executions?pipeline=Get-Microservice-Info-From-Helmfile)


## Stage Overview

This is an overview of the csar build stages, the parameters used for each section:

- Get Latest Helmfile
    * This job is used as part of multiple spinnaker flows.
    * It is used to fetch the latest version of a given helm chart or helmfile.
    * For more info on the Jenkins File see description page, [getLatestChartOrHelmfile.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/getLatestChartOrHelmfile.md)

- Get Microservice Info From Project helmfile
    * Downloads the helmfile from the repo
    * Performs a "helm build" on the downloaded helmfile
    * "Helm build" details is used to download all the applications from the helmfile.
    * Each application is extracted to get the microservice details
    * For more info on the Jenkins File see description page, [getMicroserviceInfoFromHelmfile.Jenkinsfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/getMicroserviceInfoFromHelmfile.md)


## Parameters Overview
The following is a list of parameters that are used within the file.

| Parameter         | Description                                                                                                                                                    | Default |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| EO Version        | EO Version to check the microservice for, if set to 0.0.0 latest will be fetch from the drop repo i.e. helmfile that has been released from product staging.   | 0.0.0   |
| EIAE Version      | EIAE Version to check the microservice for, if set to 0.0.0 latest will be fetch from the drop repo i.e. helmfile that has been released from product staging. | 0.0.0   |
| EOOM Version      | EOOM Version to check the microservice for, if set to 0.0.0 latest will be fetch from the drop repo i.e. helmfile that has been released from product staging. | 0.0.0   |

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
