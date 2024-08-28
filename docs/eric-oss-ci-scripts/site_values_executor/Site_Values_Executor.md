## Site Values Executor

[TOC]

## Introduction
This is the main executor for the Site Values commands.

The commands available for use through this executor are listed below.

## Execute "site_values_executor" help
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> site_values_executor --help
```

## Available commands
| Command                             | Description                                                                                   | Link                                                                             |
|-------------------------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| create-site-values-file             | Create a new site values file from a comma separated string of keys with unique values        | [Create_Site_Values_File.md](Create_Site_Values_File.md)                         |
| merge-yaml-files                    | Merge a base yaml file with an override file and output to a new file                         | [Merge_YAML_Files.md](Merge_YAML_Files.md)                                       |
| replacing-password                  | Obfuscate a cleartext registry password within a site values file                             | [Replacing_Password.md](Replacing_Password.md)                                   |
| set-deployment-tags                 | Set selected deployment tags in a site values file                                            | [Set_Deployment_Tags.md](Set_Deployment_Tags.md)                                 |
| substitute-values                   | Substitute placeholder variables contained in a site-values file with values in a config file | [Substitute_Values.md](Substitute_Values.md)                                     |
| update-site-values-file-enable-tags | Output a site-values file using a site-values base file and a list of tags to enable          | [Update_Site_Values_File_Enable_Tags.md](Update_Site_Values_File_Enable_Tags.md) |

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
