# Get Deployment Manager URL And Tag

[TOC]

## Introduction
This command is used to get the Deployment Manager tag and output it to a properties file.

The command requires three arguments to get the DM tag and output it to a properties file.
- --image
- --file
- --properties-file

If the user specifies a specific version of the Deployment Manager image, e.g. armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:1.2.3 then it will be outputted to the file.
If the user specifies the 'default' image and a valid path to the dm_version.yaml file, then the tag will be taken from there and outputted to the file.
If the user specifies the 'default' image and an INVALID path to the dm_version.yaml file then the tag will be set to 'latest' in the file

## Sample Output
```
IMAGE=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest
```

## Prerequisites
The following is a list of required prerequisites
- An untarred helmfile to access the dm_version.yaml file

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> utils_executor get-dm-url-and-tag --help
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
  utils_executor get-dm-url-and-tag \
  --image armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:default \
  --file $PWD/<HELMFILE>/dm_version.yaml \
  --properties-file $PWD/IMAGE_DETAILS.txt
```


### Available Parameters
| Parameter         | Description                                                                 | Optional or Required |
|-------------------|-----------------------------------------------------------------------------|----------------------|
| --image           | The DM image and tag to supply to the command                               | Required             |
| --file            | The path to the dm_version.yaml file in the helmfile                        | Required             |
| --properties-file | The path and name of the resulting properties file with the tag information | Required             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)      | Optional             |
| --help            | Show the help functionality for the command                                 | Optional             |

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
