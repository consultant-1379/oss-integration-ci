# Static Tests

[TOC]

## Introduction
This command is used to execute the Static Tests against a given helm chart.

## Prerequisites
The following is a list of required prerequisites
- A clone of the chart repository with the changes/TGZ File of the chart you want to test against.
- A clone of the oss-integration-ci repository within the working directory.
- Combined Site Values file generated from the "Generate Site Values" stage - Information on how to run this locally can be found on: [Generate Optionality Maximum](https://eteamspace.internal.ericsson.com/display/DGBase/Run+Helmfile+Precode+Stages+Locally+-+Generate+Optionality+Maximum).

## How to use the Docker image
The docker image, "eric-oss-ci-scripts" is built intermittently.
To ensure the latest version of the image is being used, please see the labels on the oss-integration-ci
repo for the latest available version.

Each label represents a version of the eric-oss-ci-scripts docker image.

To execute the command the following are the basic volumes and details needed,
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor static-tests --help
```

### Executing the command
The following is an example of running the command:

```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  pre_code_review_executor static-tests \
  --state-values-file $PWD/<SITE_VALUES_FILE_GENERATED> \
  --chart-full-path $PWD/<CHART_FULL_PATH> \
  --specific-skip-file $PWD/<SPECIFIC_SKIP_LIST_FILE> \
  --common-skip-file $PWD/<COMMON_SKIP_LIST_FILE> \
```

### Available Parameters
| Parameter                | Description                                                                                                                                                                                                         | Optional or Required |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --chart-full-path        | The absolute path to the directory that contains the Chart.yaml that is stored within the Chart directory.                                                                                                          | Required             |
| --state-values-file      | The absolute path to the site values file that was generated during the "Generate Site Values File" stage.                                                                                                          | Required             |
| --specific-skip-file     | The absolute path to the helmfile-specific file of static tests to be skipped. This file resides within the oss-integration-ci repository under testsuite/common/helmfile-validator/<helmfile_name>/skip_list.json. | Required             |
| --common-skip-file       | The absolute path to the file of static tests to be skipped for all Helmfiles. This file resides within the oss-integration-ci repository under testsuite/common/helmfile-validator/common-skip-list.json.          | Required             |
| --verbosity              | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                              | Optional             |
| --help                   | Show the help functionality for the command                                                                                                                                                                         | Optional             |

### Output
A report.html file will be generated within the workspace which showcases what static tests have failed/passed/skipped.

## Contacts

### Guardians

See in [Contributing Guide](../../../Contribution_Guide.md)

### Backlog

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../../../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel