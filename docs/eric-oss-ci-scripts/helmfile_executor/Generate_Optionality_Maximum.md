# Generate Optionality Maximum

[TOC]

## Introduction
The command is used to create an optionality_maximum.yaml file.

This is done by adding the data from the helmfile optionality file to a dictionary, downloading the helmfile's
dependencies to the chart cache directory and iterating over these charts to extract each optionality file to the same
dictionary. The contents of this dictionary are then merged and written to a new combined optionality_maximum yaml file.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- Artifactory User Credentials, this is used to fetch the charts from artifactory
- A chart cache directory where downloaded packages can be cached to/from
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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor generate-optionality-maximum --help
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
  --volume ${PWD}/<PATH_TO_LOCAL_PACKAGE_CACHE_DIRECTORY>:${PWD}/<MOUNTED_PACKAGE_CACHE_DIRECTORY> \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor generate-optionality-maximum \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file ${PWD}/<SITE_VALUES_FILE> \
  --chart-cache-directory <MOUNTED_PACKAGE_CACHE_DIRECTORY> \
  --artifactory-username <GERRIT_USERNAME> \
  --artifactory-password <GERRIT_PASSWORD>
```


### Available Parameters
| Parameter               | Description                                                                                                                                                                                                                       | Optional or Required |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile      | This is the full path to the helmfile under test, including the file name.                                                                                                                                                        | Required             |
| --state-values-file     | The full path to the site-values file used to template the helmfile.                                                                                                                                                              | Required             |
| --chart-cache-directory | The full path to where the downloaded packages should be cached to/from.                                                                                                                                                          | Required             |
| --artifactory-username  | This is the username to log into Artifactory. This can also be set as an environment variable, GERRIT_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --artifactory-password  | This is the user password to log into Artifactory. This can also be set as an environment variable, GERRIT_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --verbosity             | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                            | Optional             |
| --help                  | Show the help functionality for the command                                                                                                                                                                                       | Optional             |

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
  --volume $PWD/<PATH_TO_LOCAL_PACKAGE_CACHE_DIRECTORY>:$PWD/<MOUNTED_PACKAGE_CACHE_DIRECTORY> \
  --workdir $PWD \
  --env GERRIT_USERNAME \
  --env GERRIT_PASSWORD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor generate-optionality-maximum \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file <SITE_VALUES_FILE> \
  --chart-cache-directory <MOUNTED_PACKAGE_CACHE_DIRECTORY>
```

### Output
An optionality_maximum.yaml file containing the merged optionality files of the helmfile and all its charts.

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
