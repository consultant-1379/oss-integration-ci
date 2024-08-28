# Substitute Values

[TOC]

## Introduction
This command is used substitute placeholder values within a site-values YAML file with variables contained within a
config file.

## Prerequisites
The following is a list of required prerequisites
- A base site values file
- A config file containing key/value pairs representing substitutions

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> site_values_executor substitute-values --help
 ```

### Input
In addition to the base site values file which will have its values substituted a config file containing key/value pairs
representing those substitutions is also necessary. Each key represents the dummy value that will be replaced and the
corresponding value is the new value that will replace it, i.e. <PLACEHOLDER>=<VALUE>

The following is an example of the contents of such a config file:

```
dummy-repo=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
Ericsson123!=ciloopman-user-creds
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
  site_values_executor substitute-values \
  --state-values-file $PWD/<SITE_VALUES_FILE_PATH> \
  --file $PWD/<SUBSTITUTION_CONFIG_FILE_PATH>
```


### Available Parameters
| Parameter           | Description                                                                                 | Optional or Required |
|---------------------|---------------------------------------------------------------------------------------------|----------------------|
| --state-values-file | The full path to the site-values file to be used as the base to have its values substituted | Required             |
| --file              | The config file containing the key/value pairs used for replacement                         | Required             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                      | Optional             |
| --help              | Show the help functionality for the command                                                 | Optional             |

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
