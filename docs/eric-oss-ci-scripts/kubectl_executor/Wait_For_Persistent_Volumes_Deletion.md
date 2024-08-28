# Wait for Persistent Volumes Deletion

[TOC]

## Introduction
Wait for Persistent Volumes to be deleted from a specified namespace within the target cluster.

## Prerequisites
The following is a list of required prerequisites
- Access to the Kubernetes cluster via a Kubernetes Configuration file.
- A namespace that has been created, that you want to wait for persistent volumes to be deleted.

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> kubectl_executor wait-for-persistent-volumes-deletion --help
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
  kubectl_executor wait-for-persistent-volumes-deletion \
  --namespace <NAMESPACE_NAME> \
  --kubeconfig-file <KUBE_CONFIG_FILE_PATH> \
  --retries <NUMBER_OF_RETRIES_TO_CHECK_IF_PVs_ARE_DELETED> \
  --timeout <SPECIFIED_NUMBER_OF_SECONDS_THAT_YOU_WANT_TO_WAIT_BETWEEN_EACH_RETRY>
```

### Available Parameters
| Parameter         | Description                                                                | Optional or Required |
|-------------------|----------------------------------------------------------------------------|----------------------|
| --namespace       | Namespace where PVs are present that needs to be deleted.                  | Required             |
| --kubeconfig-file | Kube config file path to access target cluster.                            | Required             |
| --retries         | Maximum number of retries to perform to check if PVs are deleted.          | Required             |
| --timeout         | Time which will elapse between each retry checking if the PVs are deleted. | Required             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)     | Optional             |
| --help            | Show the help functionality for the command.                               | Optional             |

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