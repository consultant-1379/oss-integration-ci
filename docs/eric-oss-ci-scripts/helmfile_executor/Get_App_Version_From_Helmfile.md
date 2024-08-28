# Get App Version From Helmfile

[TOC]

## Introduction
The command is used to get all the application names and their versions in a helmfile, the results of which will be
written to a properties file in the form <CHART_NAME>=<CHART_VERSION>.

This is done by running the helmfile build command with the site-values file, iterating over the output and saving each
chart name and version to a list. The list is then subsequently logged and written to a properties file. A parameter
can also be set to ensure only enabled charts are included.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- A populated site-values yaml file

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor get-app-version-from-helmfile --help
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
  helmfile_executor get-app-version-from-helmfile \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file ${PWD}/<SITE_VALUES_FILE> \
  --tags-set-to-true-only <BOOLEAN_TRUE_OR_FALSE>
```


### Available Parameters
| Parameter               | Description                                                                                   | Optional or Required |
|-------------------------|-----------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile      | This is the full path to the helmfile under test, including the file name.                    | Required             |
| --state-values-file     | The full path to the site-values file used to template the helmfile.                          | Required             |
| --tags-set-to-true-only | A boolean value used to determine whether only the enabled charts are included or all charts. | Required             |
| --verbosity             | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                        | Optional             |
| --help                  | Show the help functionality for the command                                                   | Optional             |

### Output
An artifact properties file will be created with a list of all chart names and versions within the helmfile, if the
--tags-set-to-true-only parameter is set to true only enabled applications will be recorded. These values will also be
logged during execution. The following is an example of the contents of such a properties file.

```
eric-tm-ingress-controller-cr-crd=11.3.0+59
eric-mesh-controller-crd=13.0.0+50
eric-sec-sip-tls-crd=6.1.0+1
eric-oss-kf-sz-op-crd=1.2.0-4
eric-sec-certm-crd=5.0.0+18
eric-data-key-value-database-rd-crd=2.0.0+5
eric-aiml-model-lcm-crd=2.0.0-0
eric-data-wide-column-database-cd-crd=1.24.0+88
eric-sec-access-mgmt-crd=1.1.0+1
eric-storage-encryption-provider=0.17.0
eric-cloud-native-service-mesh=14.1.0
eric-cnbase-oss-config=1.23.0
eric-cloud-native-base=161.3.0
eric-cncs-oss-config=0.66.0
eric-oss-common-base=0.570.0
eric-oss-oran-support=0.98.0
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
