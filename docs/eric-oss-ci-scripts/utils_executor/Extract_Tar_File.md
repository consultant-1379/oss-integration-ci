# Extract Tar File

[TOC]

## Introduction
This command is used to extract a given tar file.

## Prerequisites
The following is a list of required prerequisites
- A tar file to extract

## Output
The following output is produced
- The extracted file
- A properties file with the name of the base directory of the extracted tar file

Sample output of properties file
```
TAR_BASE_DIR=<BASE DIR>
```

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> utils_executor extract-tar-file --help
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
  utils_executor extract-tar-file \
  --file <PATH TO TAR FILE> \
  --dir <DIRECTORY TO UNTAR THE FILE TO> \
  --properties-file <PATH TO RESULTING PROPERTIES FILE>
```


### Available Parameters
| Parameter         | Description                                                            | Optional or Required |
|-------------------|------------------------------------------------------------------------|----------------------|
| --file            | The path to the tar file to extract                                    | Required             |
| --dir             | The directory to extract the tar file to                               | Required             |
| --properties-file | The path to the resulting properties file                              | Required             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3) | Optional             |
| --help            | Show the help functionality for the command                            | Optional             |

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
