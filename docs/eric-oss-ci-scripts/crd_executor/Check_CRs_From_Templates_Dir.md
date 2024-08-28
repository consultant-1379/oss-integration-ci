# Check CRs From Templates Dir

[TOC]

## Introduction
This command is used validate CRD manifests from a specified directory using Kubeconform.

## Prerequisites
The following is a list of required prerequisites
- A directory of CRD templates
- The Kubeconform image e.g. armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-kubeconform:latest
- Run the container with root permissions i.e., --user 0:0

## How to use the Docker image
The docker image, "eric-oss-ci-scripts" is built intermittently.
To ensure the latest version of the image is being used, please see the labels on the oss-integration-ci
repo for the latest available version.

Each label represents a version of the eric-oss-ci-scripts docker image.

To execute the command the following are the basic volumes and details needed,
```
docker run \
  --init --rm \
  --user 0:0 \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume <PATH>/.docker:/root/.docker \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> crd_executor check-crs-from-templates-dir --help
 ```

### Executing the command
The following is an example of running the command
```
docker run \
  --init --rm \
  --user 0:0 \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume <PATH>/.docker:/root/.docker \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  crd_executor check-crs-from-templates-dir \
  --dir $PWD/<PATH TO TEMPLATES> \
  --image armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-kubeconform:<VERSION>
```


### Available Parameters
| Parameter   | Description                                                                 | Optional or Required |
|-------------|-----------------------------------------------------------------------------|----------------------|
| --dir       | The directory where the CRD manifests are stored.                           | Required             |
| --image     | The version of the Kubeconform image used for validating the CRD manifests. | Required             |
| --verbosity | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)      | Optional             |
| --help      | Show the help functionality for the command                                 | Optional             |

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
