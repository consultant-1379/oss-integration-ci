# Create Site Values File

[TOC]

## Introduction
This command is used to create a new site values file using a provided comma separated list of keys and associated values.

## Prerequisites
The following is a list of required prerequisites
- A correctly formatted list of key/value pairs to be used as the site values file base

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> site_values_executor create-site-values-file --help
 ```

### Input List
The format of the list used to create the site values file should be <KEY>=<VALUE>,<KEY>=<VALUE>,<KEY>=<VALUE>.
To indicate the next nested level of a key a period should be used <TOP_KEY>.<MID_KEY>.<LOW_KEY>=<VALUE>.
Additionally, no spaces should be included in the list, below is listed a more direct example:

```
eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false
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
  site_values_executor create-site-values-file \
  --optional-key-value-list <KEY_VALUE_LIST> \
  --path-output-yaml <PATH_TO_SITE_VALUES_FILE>
```


### Available Parameters
| Parameter                 | Description                                                                                                                            | Optional or Required |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --optional-key-value-list | List of keys and associated values used to populate the newly created site values file, example listed above in the Input List section | Required             |
| --path-output-yaml        | The full path to where the new site values file will be created including the new file's name                                          | Required             |
| --verbosity               | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                 | Optional             |
| --help                    | Show the help functionality for the command                                                                                            | Optional             |

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
