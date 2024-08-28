# Get Base Baseline

[TOC]

## Introduction
The command is used to get the Base Baseline names and versions of applications from a helmfile or set a new Base
Baseline using an input file.

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor get-base-baseline --help
 ```

### Input File
When setting the baseline for a chart an input file must be provided, this contains details of a chart's name, version
and repository that will be set as the chart's new baseline. An example of the contents is provided below:

```
CHART_NAME=eric-oss-common-base
CHART_VERSION=0.681.0
CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
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
  helmfile_executor get-base-baseline \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --project-file-name <PROJECT_FILE_NAME> \
  --execution-type <GET_OR_SET_BASELINE> \
  --input-file <INPUT_FILE_PATH> \
  --output-file <OUTPUT_FILE_PATH>
```


### Available Parameters
| Parameter           | Description                                                                                                                               | Optional or Required |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile  | This is the full path to the helmfile under test, including the file name                                                                 | Required             |
| --project-file-name | The project file name to check if set within the helmfiles, e.g. eric-eiae-helmfile                                                       | Required             |
| --execution-type    | Sets the type of execution, either get_baseline to set a new baseline or set_baseline to create a new one                                 | Required             |
| --input-file        | Stores the content of the helm chart details to swap for the current version, if any is supplied, has a default value of input.properties | Optional             |
| --output-file       | File where the execution's output is stored, has a default value of artifact.properties                                                   | Optional             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                    | Optional             |
| --help              | Show the help functionality for the command                                                                                               | Optional             |

### Output
An output file will be created named according to the output-file parameter or artifact.properties if none is provided.
This file will list all the charts' names, versions and repositories within the base baseline. The same details
for the baseline itself and the baseline charts will also be listed in a csv format. An example of the output is
listed below:

```
eric-service-exposure-framework_name=eric-service-exposure-framework
eric-service-exposure-framework_version=0.76.0
eric-service-exposure-framework_repo=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
eric-cloud-native-service-mesh_name=eric-cloud-native-service-mesh
eric-cloud-native-service-mesh_version=16.2.0
eric-cloud-native-service-mesh_repo=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/
eric-cnbase-oss-config_name=eric-cnbase-oss-config
eric-cnbase-oss-config_version=1.28.0
eric-cnbase-oss-config_repo=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local
...
eric-sec-access-mgmt-crd_name=eric-sec-access-mgmt-crd
eric-sec-access-mgmt-crd_version=1.1.0+1
eric-sec-access-mgmt-crd_repo=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm
BASE_PLATFORM_BASELINE_CHART_NAME=eric-service-exposure-framework, eric-cloud-native-service-mesh, eric-cnbase-oss-config, eric-cloud-native-base, eric-cncs-oss-config, eric-oss-common-base, eric-mesh-controller-crd, eric-sec-sip-tls-crd, eric-sec-certm-crd, eric-data-key-value-database-rd-crd, eric-data-wide-column-database-cd-crd, eric-sec-access-mgmt-crd
BASE_PLATFORM_BASELINE_CHART_VERSION=0.76.0, 16.2.0, 1.28.0, 181.2.0, 0.77.0, 0.679.0, 14.0.0+73, 6.1.0+1, 5.0.0+18, 2.0.0+7, 1.24.0+88, 1.1.0+1
BASE_PLATFORM_BASELINE_CHART_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm
BASE_PLATFORM_BASELINE_NAME=base-platform-baseline
BASE_PLATFORM_BASELINE_VERSION=0.492.0
BASE_PLATFORM_BASELINE_REPO=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm
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
