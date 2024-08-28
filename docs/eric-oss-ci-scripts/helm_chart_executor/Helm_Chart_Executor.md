## Helm Chart Executor

[TOC]

## Introduction
This is the main executor for the Helm Chart commands.

The commands available for use through this executor are listed below.

## Execute "helm_chart_executor" help
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helm_chart_executor --help
```

## Available commands
| Command                                        | Description                                                                            | Link                                                                                                   |
|------------------------------------------------|----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| helm-chart-package                             | This command packages a chart into a versioned chart archive file                      | [Helm_Chart_Package.md](Helm_Chart_Package.md)                                                         |
| remove-releases                                | Remove releases from a given namespace                                                 | [Remove_Releases.md]( Remove_Releases.md)                                                              |
| remove-sep-release                             | Remove Storage Encryption Provider from Namespace                                      | [Remove_SEP_Release.md](Remove_SEP_Release.md)                                                         |
| compare-microservice-versions-from-application | Compare Microservice versions from a chart to the latest versions in the relevant repo | [Compare_Microservice_Versions_From_Application.md](Compare_Microservice_Versions_From_Application.md) |
| cncs-optionality-checker                       | Check the CNCS optionality values                                                      | [CNCS_Optionality_Checker.md](CNCS_Optionality_Checker.md)                                             |

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
