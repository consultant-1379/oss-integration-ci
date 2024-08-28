## Confluence Executor

[TOC]

## Introduction
This is the main executor for Confluence commands.

It facilitates interactions with Confluence and Jira, such as copying documentation stored in a gerrit repository
over to Confluence and creating Jira tickets with a specific template.

## Execute "confluence_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> confluence_executor --help
```

## Available commands
| Command                                  | Description                                                                                              | Link                                                                               |
|------------------------------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Confluence_Transfer_Gerrit_Documents     | Used to Copy documentation Markdown files from a given directory to a specified Confluence space         | [Confluence_Transfer_Gerrit_Documents.md](Confluence_Transfer_Gerrit_Documents.md) |
| Confluence_Create_Outdated_Image_Tickets | Used to Create a number of Jira tickets listing the charts with outdated images for a specified helmfile | [Create_Outdated_Image_Tickets.md](Confluence_Create_Outdated_Images_Tickets.md)   |

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
