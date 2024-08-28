## CI Helm Executor

[TOC]

## Introduction
This is the main executor for the CI Helm commands.

It uses the ADP enabler, cihelm to fetch and package charts, see more info on ADP's CI Helm
[here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/pc/cihelm/+/refs/heads/master/README.md).
The main goal of this enabler is to essentially fetch or package a helm chart as fast as the network and remote helm
repositories allow. The cihelm commands eliminates the helm repo add and helm repo update commands.

## Execute "cihelm_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> cihelm_executor --help
```

## Available commands
| Command                   | Description                                                                                                               | Link                                                           |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| cihelm-fetch              | Used to Fetch Chart Dependency from a given helmfile.                                                                     | [CI-Helm_Fetch.md](CI-Helm_Fetch.md)                           |
| cihelm-fetch-single-chart | Used to download a single helm chart from a repo.                                                                         | [CI-Helm_Fetch_Single_Chart.md](CI-Helm_Fetch_Single_Chart.md) |
| cihelm-package            | Used to Package a helm Chart against a given helm chart repo. Allows the setting of the appropriate version for packaging | [CI-Helm_Package.md](CI-Helm_Package.md)                       |

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
