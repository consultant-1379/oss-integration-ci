## CSAR Executor

[TOC]

## Introduction
This is the main executor for the CSAR commands.

The Cloud Service Archive (CSAR) is a packaging format used to deploy cloud-native applications. The CSAR
should contain all of the necessary components to deploy a cloud-native application, such as code, dependencies,
and metadata. The commands in this executor are used for CSAR-related operations.

## Execute "csar_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> csar_executor --help
```

## Available commands
| Command                              | Description                                                                                                            | Link                                                                               |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Check_For_Existing_CSAR              | Used to check if a specific CSAR exists in a given repository                                                          | [Check_For_Existing_CSAR.md](Check_For_Existing_CSAR.md)                           |
| Combine_CSAR_Build_Info              | Combine the information from a CSAR's images.txt and manifest.txt files                                                | [Combine_CSAR_Build_Info.md](Combine_CSAR_Build_Info.md)                           |
| Compare_CSAR_and_Helmfile_Images     | Compare the images within a CSAR to the images within a helmfile for that CSAR                                         | [Compare_CSAR_and_Helmfile_Images.md](Compare_CSAR_and_Helmfile_Images.md)         |
| Download_and_Compare_CSAR_Build_Info | Download a CSAR's manifest.txt from a given repository and compare it against the manifest.txt of a locally built CSAR | [Download_and_Compare_CSAR_Build_Info.md](Download_and_Compare_CSAR_Build_Info.md) |
| Download_Existing_CSAR               | Download an existing CSAR from a given repository                                                                      | [Download_Existing_CSAR.md](Download_Existing_CSAR.md)                             |

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
