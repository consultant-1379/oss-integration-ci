# Remove Storage Encryption Provider (SEP) Release

[TOC]

## Introduction
This command is used to remove a Storage Encryption Provider release from specified Namespace

## Prerequisites
- Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST, otherwise fetch kube config from the jenkins credentials.
- A Kuberenetes namespace where Storage Encryption Provider release is stored
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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helm_chart_executor remove_sep_release --help
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
  helm_chart_executor remove_sep_release \
  --namespace <NAMESPACE> \
  --kubeconfig-file <kube-config-path>
```


### Available Parameters
| Parameter               | Description                                                                                                                                                                    | Optional or Required |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --namespace             | Namespace to purge deployment environment                                                                                                                                      | Required             |
| --kubeconfig-file       | Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename included the extension stored in OST. | Required             |
| --verbosity             | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                         | Optional             |
| --help                  | Show the help functionality for the command                                                                                                                                    | Optional             |

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