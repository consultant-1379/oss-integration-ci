# Get Secret or ConfigMap data from key submitted

[TOC]

## Introduction
Can be used to get data from a secret or configmap according to a search string inputted. data is returned in an
artifact.properties file

## Prerequisites
The following is a list of required prerequisites
- Access to the Kubernetes cluster via a Kubernetes Configuration file.
- A namespace that has been created, that you want to get data from a pre existing resource, secret or configmap.

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> kubectl_executor get-value-from-configmap-or-secret  --help
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
  kubectl_executor get-value-from-configmap-or-secret \
  --namespace <NAMESPACE_NAME> \
  --kubeconfig-file <KUBE_CONFIG_FILE_PATH> \
  --resource-type <secret or configmap> \
  --resource-name <created resource name>
  --search-string <Key from secret or config data to return the value>
```

### Available Parameters
| Parameter         | Description                                                                            | Optional or Required |
|-------------------|----------------------------------------------------------------------------------------|----------------------|
| --namespace       | Namespace where you want to create the generic secret on.                              | Required             |
| --kubeconfig-file | Kube config file path to access target cluster.                                        | Required             |
| --resource-name   | Used to specify a Kubernetes resource name                                             | Required             |
| --resource-type   | Used to specify a Kubernetes resource type, "secret", "configmap".                     | Required             |
| --search-string   | Used to set a search string. This should be a key that exists in the resource          | Required             |
| --recreate-secret | A boolean value to indicate whether the secret is to be recreated if already existing. | Optional             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                 | Optional             |
| --help            | Show the help functionality for the command                                            | Optional             |

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
