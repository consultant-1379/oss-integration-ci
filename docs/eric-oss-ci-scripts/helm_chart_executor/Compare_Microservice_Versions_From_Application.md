# Compare Microservice Versions From Application

[TOC]

## Introduction
This command is used to compare the Microservice versions in an Application chart to the latest from the relevant repository.
This is done by:
- Downloading the chart.
- Extract the content of the Chart tar file.
- Populate the dict with the Microservice information for the given chart name.
- Compare component versions in an Application to the latest from the relevant repository.

## Prerequisites
- Artifactory User Credentials, this is used to fetch the charts from artifactory
- A populated site-values yaml file
- Chart tar file
- Downloaded helmfile with chart name, version and repo


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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helm_chart_executor compare_microservice_versions_from_application --help
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
  helm_chart_executor compare-microservice-versions-from-application \
  --state-values-file ${PWD}<SITE_VALUES_FILE> \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --chart-name <CHART_NAME> \
  --chart-repo <CHART_REPO> \
  --chart-version <CHART_VERSION>
  --username <FUNCTIONAL_USER_USERNAME>  \
  --user-password <FUNCTIONAL_USER_PASSWORD> \
  --gerrit-password <GERRIT_PASSWORD> \
  --gerrit-username <GERRIT_USERNAME > \
```

### Available Parameters
| Parameter           | Description                                                                                                                                                                                                                                | Optional or Required |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --chart-name        | The name of the application chart to compare the microservice version e.g.eric-data-document-database-pg                                                                                                                                   | Required             |
| --chart-version     | The version of the Chart used to compare its microservice versions e.g. 0.0.0                                                                                                                                                              | Required             |
| --chart-repo        | The repository in which the application chart is stored, e.g. https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local<br/>                                                                                              | Required             |
| --state-values-file | The full path to the site-values file used to template the helmfile.                                                                                                                                                                       | Required             |
| --path-to-helmfile  | This is the full path to the helmfile under test, including the file name.                                                                                                                                                                 | Required             |
| --username          | This is the username to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --user-password     | This is the user password to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --gerrit-username   | This is the username to log into Artifactory. This can also be set as an environment variable, GERRIT_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.               | Required             |
| --gerrit-password   | This is the username to log into Artifactory. This can also be set as an environment variable, GERRIT_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.               | Required             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                     | Optional             |
| --help              | Show the help functionality for the command                                                                                                                                                                                                | Optional             |


### Set an Environment variable.
The environment variable should be set prior to executing the docker image and in the same shell.

To set an environment variable, execute the export command
```
export COMMAND="true"
```
The above will set "COMMAND" to true for the rest of the shell life. This variable will be available now in the global
environment variables when needed. To see all environment variables execute "env" on the shell.

### Environment Variables Associated to this Command.
The following is a list of global environments variables that can be set prior to executing the command.
They are the Artifactory credentials required for downloading the chart.
They can be set as environment variables here, or passed in as username and password arguments as shown in examples above.
  - export GERRIT_USERNAME="\<name>"
  - export GERRIT_PASSWORD="\<password>"
  - export FUNCTIONAL_USER_USERNAME="\<name>"
  - export FUNCTIONAL_USER_PASSWORD="\<password>"

If adding these parameters as environment variables, extra config is required on the docker run command to pass the
environment variables i.e. "--env <VARIABLE>" to the docker image during execution.

See example below
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  --env <FUNCTIONAL_USER_PASSWORD> \
  --env <FUNCTIONAL_USER_USERNAME> \
  --env <GERRIT_PASSWORD> \
  --env <GERRIT_USERNAME > \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helm_chart_executor compare-microservice-versions-from-application \
  --state-values-file ${PWD}<SITE_VALUES_FILE> \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --chart-name <CHART_NAME> \
  --chart-repo <CHART_REPO> \
  --chart-version <CHART_VERSION>
```
### Output
A pair of properties files:
- component_name_repo_version.csv
- component_version_mismatch.txt

See example output below for the component_name_repo_version.csv:

| Component                      | Current Version        | Latest Version | Repo                                                               |
|--------------------------------|------------------------|----------------|--------------------------------------------------------------------|
| eric-data-document-database-pg |  7.5.0+50              | 9.2.0-44       | https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm/ |

See example output below for the component_version_mismatch.txt:
```
Version mismatch: eric-data-document-database-pg
Current version: 7.5.0+50
Latest version: 9.2.0-44

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