# Download Helmfile

[TOC]

## Introduction
The command is used to download a helmfile of a given name and version from artifactory.

This is done by first defining the full chart name and url, then making a HTTP request to artifactory using those and
the artifactory authentication. Finally if the request is successful the response content is written to a .tgz file
of with the filename of the helmfile's name and version.

## Prerequisites
The following is a list of require prerequisites
- Functional User Credentials, this is used to fetch the charts from artifactory

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor download-helmfile --help
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
  helmfile_executor download-helmfile \
  --chart-name <CHART_NAME> \
  --chart-version <CHART_VERSION> \
  --chart-repo <CHART_REPO> \
  --username <FUNCTIONAL_USER_USERNAME> \
  --user-password <FUNCTIONAL_USER_PASSWORD>
```


### Available Parameters
| Parameter       | Description                                                                                                                                                                                                                                | Optional or Required |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --chart-name    | The name of the helmfile to be downloaded, e.g. eric-oss-common-base                                                                                                                                                                       | Required             |
| --chart-version | The version of the helmfile to be downloaded, e.g. 0.0.0                                                                                                                                                                                   | Required             |
| --chart-repo    | The repository in which the helmfile is stored, e.g. https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local                                                                                                            | Required             |
| --username      | This is the username to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --user-password | This is the user password to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --verbosity     | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                     | Optional             |
| --help          | Show the help functionality for the command                                                                                                                                                                                                | Optional             |

## Hiding Sensitive Information
Sometimes it may be necessary to ensure sensitive information is not displayed in a console. This can be achieved with
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
  - export FUNCTIONAL_USER_USERNAME="\<name>"
  - export FUNCTIONAL_USER_PASSWORD="\<password>"

If adding these parameters as environment variables, extra config is required on the docker run command to pass the
environment variables i.e. "--env <VARIABLE>" to the docker image during execution.

See example below
```
  docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --env FUNCTIONAL_USER_USERNAME \
  --env FUNCTIONAL_USER_PASSWORD \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor compare-application-versions-from-helmfile \
  --chart-name <CHART_NAME> \
  --chart-version <CHART_VERSION> \
  --chart-repo <CHART_REPO
```

### Output
A helmfile .tgz file in the format of <CHART_NAME>-<CHART_VERSION>.tgz, e.g. eric-eiae-helmfile-2.2828.0.tgz

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
