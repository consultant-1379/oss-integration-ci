# Check Helmfile Deployment

[TOC]

## Introduction
The command is used to verify the helmfile deployment status within a given namespace using the helmfile's site values
template, a deployment tag list, a list of optional tags and an optional list of key/value sets.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- An associated active deployment with a kubeconfig file
- A list of deployment tags

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor check-helmfile-deployment --help
 ```

### Executing the command
The following is an example of running of the command
- Extract the helmfile tar file in the current working directory.
- Execute the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor check-helmfile-deployment \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --deployment-tags <LIST_OF_DEPLOYMENT_TAGS> \
  --optional-tags <LIST_OF_OPTIONAL_TAGS> \
  --optional-key-value-list <OPTIONAL_LIST_OF_KEY_VALUE_PAIRS> \
  --namespace <NAMESPACE> \
  --kubeconfig-file <KUBECONFIG_FILE> \
  --check-tags <TAGS_LIST> \
  --check-full-version <BOOLEAN_TRUE_OR_FALSE>
```


### Available Parameters
| Parameter                 | Description                                                                                                                                                                                                                                           | Optional or Required |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile        | This is the full path to the helmfile under test, including the file name                                                                                                                                                                             | Required             |
| --deployment-tags         | Space separated list of tags to include in general deployment checks, e.g. eoEvnfm eoVmvnfm eoCm                                                                                                                                                      | Required             |
| --optional-tags           | Space separated list of optional tags to include in general deployment checks, can be ignored by setting as empty string                                                                                                                              | Required             |
| --optional-key-value-list | Comma-separated list of optional key/value groups to add to site values, can be ignored by setting as 'None', e.g. eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false | Required             |
| --namespace               | Target namespace for existing deployed releases                                                                                                                                                                                                       | Required             |
| --kubeconfig-file         | The config file for the target cluster for helm operations                                                                                                                                                                                            | Required             |
| --check-tags              | Space-separated list of specific tags to use for comparing deployed vs. helmfile chart-versions                                                                                                                                                       | Required             |
| --check-full-version      | A true/false string used to toggle full versions for chart deployment checks                                                                                                                                                                          | Required             |
| --verbosity               | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                                | Optional             |
| --help                    | Show the help functionality for the command                                                                                                                                                                                                           | Optional             |

### Output
An artifact properties file will be created with a SKIP_DELETION variable (skipping the deletion of the system) set to
true or false if the checks succeeded or failed. The deployed releases will also be listed in the file similarly to
below:

```
SKIP_DELETION=false
eric-cloud-native-base-181.2.0
eric-cloud-native-service-mesh-16.2.0
eric-cnbase-oss-config-1.27.0
eric-cncs-oss-config-0.76.0
eric-eo-act-cna-1.41.0-89
eric-eo-cm-1.41.0-260
eric-eo-config-0.0.0-1
eric-oss-common-base-0.667.0
eric-oss-function-orchestration-common-0.16.0-14
```


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
