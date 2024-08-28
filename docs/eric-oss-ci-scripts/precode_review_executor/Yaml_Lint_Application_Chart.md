# Yaml Lint

[TOC]

## Introduction
This command takes a path to a chart and runs a series of linting tests to verify that the chart is well-formed through the Yamllint command.

## Prerequisites
The following is a list of required prerequisites:
- Path to the chart under test
- Path to the site values file used within the helm template command when linting (testsuite/helm-chart-validator/ directory from the repo under test).
- Yamllint Configuration File

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor yaml-lint-application-chart --help
```

### Executing the command
The following is an example of running the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  pre_code_review_executor yaml-lint-application-chart \
  --chart-full-path $PWD/<CHART_PATH> \
  --state-values-file $PWD/<TESTSUITE_SITE_VALUES_FILE> \
  --yamllint-config $PWD/<FULL_PATH_TO_YAMLLINT_CONFIGURATION_FILE> \
  --template-output-file-path $PWD/<HELM_TEMPLATE_OUTPUT_FILE_PATH> \
  --yamllint-log-file $PWD/<YAMLLINT_LOG_OUTPUT_FILE_PATH>
```

### Available Parameters
| Parameter                   | Description                                                                                                | Optional or Required |
|-----------------------------|------------------------------------------------------------------------------------------------------------|----------------------|
| --chart-full-path           | The absolute path to the directory that contains the Chart.yaml that is stored within the Chart directory. | Required             |
| --state-values-file         | The absolute path to the site-values file to template the helmfile                                         | Required             |
| --yamllint-config           | Path to Yamllint Configuration File which extends rules when running the yamllint command                  | Required             |
| --template-output-file-path | Path where helmfile template output will be saved to                                                       | Required             |
| --yamllint-log-file         | Path where yamllint output will be saved to                                                                | Required             |
| --verbosity                 | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                     | Optional             |
| --help                      | Show the help functionality for the command                                                                | Optional             |

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