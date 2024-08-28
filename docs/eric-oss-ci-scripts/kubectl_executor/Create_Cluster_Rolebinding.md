# Create Cluster Rolebinding

[TOC]

## Introduction
Creates a Cluster Rolebinding within the target cluster (Namespace does not need to be specified as cluster role bindings are global).

## Prerequisites
The following is a list of required prerequisites
- Access to the Kubernetes cluster via a Kubernetes Configuration file.

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> kubectl_executor create-cluster-rolebinding --help
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
  kubectl_executor create-cluster-rolebinding \
  --kubeconfig-file <KUBE_CONFIG_FILE_PATH> \
  --name <NAME_OF_CLUSTER_ROLEBINDING_TO_BE_CREATED> \
  --cluster-role <NAME_OF_CLUSTER_ROLE_TO_USE_IN_CLUSTER_ROLE_BINDING> \
  --service-account <NAME_OF_SERVICE_ACCOUNT_TO_USE_IN_CLUSTER_ROLE_BINDING>
```

### Available Parameters
| Parameter         | Description                                                                                                                                               | Optional or Required |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --kubeconfig-file | Kube config file path to access target cluster.                                                                                                           | Required             |
| --name            | Name of the Cluster Rolebinding to be created within the target cluster. Will not create the Cluster Role Binding if one of the same name already exists. | Required             |
| --cluster-role    | Cluster Role to use for Rolebinding.                                                                                                                      | Required             |
| --service-account | Service Account to use for Rolebinding.                                                                                                                   | Required             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                    | Optional             |
| --help            | Show the help functionality for the command                                                                                                               | Optional             |

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
