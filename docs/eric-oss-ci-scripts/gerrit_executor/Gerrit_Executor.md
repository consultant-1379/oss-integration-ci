## CSAR Executor

[TOC]

## Introduction
This is the main executor for the Gerrit commands.

Gerrit is a code collaboration tool. Gerrit stores different Git repositories, where users can easily
clone, edit, and push code changes. These changes can then be reviewed by other users, and any changes
made to the repositories can be tracked.

## Execute "gerrit_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> gerrit_executor --help
```

## Available commands
| Command                         | Description                                                                                                            | Link                                                                     |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| check-gerrit-review-submittable | Used to determine if a Gerrit change can be submitted                                                                  | [Check_Gerrit_Review_Submittable.md](Check_Gerrit_Review_Submittable.md) |
| generate-gerrit-patch           | Used to generate a new patch set on Gerrit                                                                             | [Generate_Gerrit_Patch.md](Generate_Gerrit_Patch.md)                     |

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
