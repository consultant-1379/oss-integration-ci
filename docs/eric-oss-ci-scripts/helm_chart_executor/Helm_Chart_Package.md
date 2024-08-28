# Helm Chart Package

[TOC]

## Introduction
The command is used to package a helm chart, it will fetch all the charts dependencies listed in the chart and generate
chart tar file.


## Prerequisites
The following is a list of required prerequisites
- Artifactory User Credentials, this is used in the repositories.yaml to set the username and password
to fetch the charts from artifactory.
- Directory/Repo where a Chart.yaml and associated file to generate a package.

## How to use the Docker image
The docker image, "eric-oss-ci-scripts" is built intermittently.
To ensure the latest version of the image is being used, please see the labels on the oss-integration-ci
repo for the latest available version.
To execute the command the following are the basic volumes and details needed,
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helm_chart_executor helm_chart_package --help
 ```

### Executing the command
The following is an example of running the command
- Execute the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=$PWD \
  --env HELM_CONFIG_HOME=$PWD \
  --volume $PWD/cachedir/:$PWD/cachedir/ \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helm_chart_executor helm-chart-package \
  --path-to-chart ${PWD}/<PATH_TO_CHART> \
  --directory-path ${PWD}/<PATH_TO_DIRECTORY>\
  --use-dependency-cache <TRUE_OR_FALSE> \
  --dependency-cache-directory <PATH_TO_CACHEDIR> \
  --gerrit-username <GERRIT_USERNAME> \
  --gerrit-password <GERRIT_PASSWORD>
```


### Available Parameters
| Parameter                    | Description                                                                                                                                                                                                                       | Optional or Required |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-chart              | This is the full path to the chart under test, excluding the chart file name.                                                                                                                                                     | Required             |
| --directory-path             | This is the directory to save the chart tar file to                                                                                                                                                                               | Required             |
| --version                    | This is the version the user would like to set the newly built chart to.                                                                                                                                                          | Required             |
| --use-dependency-cache       | If set to true, it uses the dependency cache directory to push and pull dependency from. default=True                                                                                                                             | Optional             |
| --dependency-cache-directory | This is the path for the directory from where are dependencies are pushed and pull from. default=/tmp/cachedir                                                                                                                    | Optional             |
| --gerrit-username            | This is the username to log into Artifactory. This can also be set as an environment variable, GERRIT_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --gerrit-password            | This is the user password to log into Artifactory. This can also be set as an environment variable, GERRIT_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --verbosity                  | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                            | Optional             |
| --help                       | Show the help functionality for the command                                                                                                                                                                                       | Optional             |


## Hiding Sensitive Information
Sometimes it maybe necessary to ensure sensitive information is not displayed in a console. This can be achieved with
the use of environment variables.

### Set a Environment variable.
The environment variable should be set prior to the executing of the docker image and in the same shell.

To set and environment variable, execute the export command
```
export COMMAND="true"
```
The above will set "COMMAND" to true for the rest of the shell life. This variable will be available now in the global
environment variables when needed. To see all environment variables execute "env" on the shell.

### Environment Variables Associated to this Command.
The following is a list of global environments variables that can be set prior to executing the command
  - export GERRIT_USERNAME="\<name>"
  - export GERRIT_PASSWORD="\<password>"

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
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=$PWD \
  --env HELM_CONFIG_HOME=$PWD \
  --volume $PWD/cachedir/:$PWD/cachedir/ \
  --env GERRIT_USERNAME \
  --env GERRIT_PASSWORD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helm_chart_executor helm-chart-package \
  --path-to-chart ${PWD}/<PATH_TO_CHART> \
  --directory-path ${PWD}/<PATH_TO_DIRECTORY> \
  --use-dependency-cache <TRUE_OR_FALSE> \
  --dependency-cache-directory <PATH_TO_CACHEDIR>
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
