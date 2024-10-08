# Merge YAML Files

[TOC]

## Introduction
This command is used to merge the contents of a base YAML file with that of one or more override files and output the
contents to a new file, provided the override file(s) are of the same structure as the base file.

## Prerequisites
The following is a list of required prerequisites
- A base yaml file
- One or more override yaml files

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> site_values_executor merge-yaml-files --help
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
  site_values_executor merge-yaml-files \
  --path-base-yaml $PWD/<PATH_TO_BASE_YAML_FILE> \
  --path-override-yaml $PWD/<PATH_TO_OVERRIDE_YAML_FILE> \
  --path-output-yaml $PWD/<PATH_TO_FINAL_OUTPUT_YAML_FILE> \
  --check-values-only <TRUE_OR_FALSE>
```


### Available Parameters
| Parameter            | Description                                                                                                                                                                     | Optional or Required |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-base-yaml     | The full path to the yaml file to be used as the base to be updated                                                                                                             | Required             |
| --path-override-yaml | The full path to the yaml file used to override the base file, a comma separated list of multiple yaml files can also be used                                                   | Required             |
| --path-output-yaml   | The full path to the output state values file generated by the operation                                                                                                        | Required             |
| --check-values-only  | If set to true will log a warning if an override key is missing from the base and an will log an error if the base contains a key not present in the override, default is false | Required             |
| --verbosity          | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                          | Optional             |
| --help               | Show the help functionality for the command                                                                                                                                     | Optional             |

## Contacts

### Guardians

See in [Contributing Guide](../../Contribution_Guide.md)

### Backlog

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
