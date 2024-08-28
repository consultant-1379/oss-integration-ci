# Validate Chart Against Schema File

[TOC]

## Introduction
Runs the helm template command using the files (Specified with search string) as values to pass into the helm template command with the chart path in order to validate the schema tests.

## Prerequisites
The following is a list of required prerequisites
- A clone of the chart repository with the changes/TGZ File of the chart you want to test against.
- A directory that contains positive and negative schema testing files (Normally placed inside the Chart).

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor validate-chart-against-schema-file --help
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
  pre_code_review_executor validate-chart-against-schema-file \
  --chart-full-path $PWD/<CHART_FULL_PATH> \
  --directory-path $PWD/<SCHEMA_TESTS_PATH> \
  --search-string yaml
  --ignore-strings "None"
```

### Available Parameters
| Parameter         | Description                                                                                             | Optional or Required |
|-------------------|---------------------------------------------------------------------------------------------------------|----------------------|
| --chart-full-path | The path to the chart that the tests should be executed against.                                        | Required             |
| --directory-path  | The path to the directory to search for the schema files to test against (Within the chart repository). | Required             |
| --search-string   | The string that is used to search for the files in the given directory.                                 | Required             |
| --ignore-strings  | A comma separated list of strings to ignore if found with the search_string.                            | Optional             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                  | Optional             |
| --help            | Show the help functionality for the command                                                             | Optional             |

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