# Check Helmfile Versions Against Given Versions

[TOC]

## Introduction
The command is used to compare a provided list of chart versions against the charts of the same names within a
helmfile.

The provided chart names and versions are used to create a dictionary of charts, then another dictionary of
charts and versions within the helmfile is created using the helmfile list command before the two are compared via
subsets. The outcome of this comparison is written to a properties file and in the event there are any differences in
versions they will be logged.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- A list of chart names and associated versions
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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor check-helmfile-versions-against-given-versions --help
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
  helmfile_executor check-helmfile-versions-against-given-versions \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file ${PWD}/<STATE_VALUES_FILE> \
  --chart-name <COMMA_SEPARATED_LIST_OF_CHART_NAMES> \
  --chart-version <COMMA_SEPARATED_LIST_OF_CHART_VERSIONS>
```


### Available Parameters
| Parameter           | Description                                                                                                                  | Optional or Required |
|---------------------|------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile  | This is the full path to the helmfile under test, including the file name.                                                   | Required             |
| --state-values-file | The full path to the site-values file used to template the helmfile.                                                         | Required             |
| --chart-name        | A comma separated list of the names of the charts whose versions are being checked, e.g. eric-oss-dmm, eric-oss-kf-sz-op-crd | Required             |
| --chart-version     | A comma separated list of the versions of the charts to be checked against the helmfile, e.g. 0.605.0, 1.2.0-4               | Required             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                       | Optional             |
| --help              | Show the help functionality for the command                                                                                  | Optional             |

### Output
A properties file called helmfile-version-check.properties will always be created.

In the event of differences between the provided chart versions and those in the helmfile, the differences will be
listed in the log and 'NO_CHART_VERSION_CHANGES=False' will be written to the properties file.
If there are no differences a warning will be displayed that all chart versions are already in the helmfile and
'NO_CHART_VERSION_CHANGES=True' will be written to the properties file.

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
