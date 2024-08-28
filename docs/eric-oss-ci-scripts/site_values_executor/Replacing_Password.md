# Replacing Password

[TOC]

## Introduction
This command is used to obfuscate a cleartext registry password within a site-values yaml file. If no registry password
is contained within the file this will be logged. Finally, the parsed yaml file in its entirety will be logged.

## Prerequisites
The following is a list of required prerequisites
- An existing site values file containing registry credentials

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> site_values_executor replacing-password --help
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
  site_values_executor replacing-password \
  --state-values-file <PATH_TO_SITE_VALUES_FILE>
```


### Available Parameters
| Parameter           | Description                                                                          | Optional or Required |
|---------------------|--------------------------------------------------------------------------------------|----------------------|
| --state-values-file | The full path to the site-values file with a functional user password to be obscured | Required             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)               | Optional             |
| --help              | Show the help functionality for the command                                          | Optional             |

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
