## CRD Executor

[TOC]

## Introduction
This is the main executor for the CRD commands.

The commands available for use through this executor are listed below.

## Execute "crd_executor" help
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> crd_executor --help
```

## Available commands
| Command                      | Description                                                                                                                       | Link                                                               |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| check-crs-from-templates-dir | Validate CRD manifests from a specified directory using Kubeconform                                                               | [Check_CRs_From_Templates_Dir.md](Check_CRs_From_Templates_Dir.md) |
| get-crd-details-from-chart   | Retrieve CRD details from a chart and generate a new property file with chart details                                             | [Get_CRD_Details_From_Chart.md](Get_CRD_Details_From_Chart.md)     |
| remove-crd-components        | Delete CRD components                                                                                                             | [Remove_CRD_Components.md](Remove_CRD_Components.md)               |
| update-crds-helmfile         | Update releases in the crds-helmfile with 'installed: true', where the installation of the release is dependent on certain 'tags' | [Update_CRDs_Helmfile.md](Update_CRDs_Helmfile.md)                 |

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
