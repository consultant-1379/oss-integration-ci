# Get Release Details From Helmfile

[TOC]

## Introduction
The command is used to fetch the CSAR descriptions and releases from a helmfile.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- A populated site-values yaml file
- A chart cache directory where downloaded packages can be cached to/from
- Functional User Credentials, this is used to fetch the helmfile from artifactory

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor get-release-details-from-helmfile --help
 ```

### Executing the command
The following is an example of running of the command
- Extract the helmfile tar file in the current working directory.
- Execute the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=${env.PWD} \
  --env HELM_CONFIG_HOME=${env.PWD} \
  --volume ${PWD}/<DEPENDENCY_CACHE_DIRECTORY>:/<DEPENDENCY_CACHE_DIRECTORY> \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor get-release-details-from-helmfile \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file ${PWD}/<SITE_VALUES_FILE> \
  --get-all-images <NUMBER_OF_DAYS> \
  --fetch-charts <BOOLEAN_TRUE_OR_FALSE> \
  --chart-cache-repository ${PWD}/<PATH_TO_DEPENDENCY_CACHE_DIRECTORY> \
  --helmfile-url <FULL_HELMFILE_URL> \
  --username <FUNCTIONAL_USER_USERNAME> \
  --user-password <FUNCTIONAL_USER_PASSWORD>
```


### Available Parameters
| Parameter                | Description                                                                                                                                                                                                                               | Optional or Required |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile       | This is the full path to the helmfile under test, including the file name                                                                                                                                                                 | Required             |
| --state-values-file      | The full path to the site-values file used to template the helmfile                                                                                                                                                                       | Required             |
| --get-all-images         | A boolean value that determines whether to include all CSARs tied to the helmfile or just installed ones                                                                                                                                  | Required             |
| --fetch-charts           | A boolean value that determines whether charts should be downloaded                                                                                                                                                                       | Required             |
| --chart-cache-repository | The full path to the dependency chart cache directory                                                                                                                                                                                     | Required             |
| --helmfile-url           | The URL of the helmfile repo                                                                                                                                                                                                              | Required             |
| --username               | This is the username to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable      | Required             |
| --user-password          | This is the user password to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable | Required             |
| --verbosity              | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                    | Optional             |
| --help                   | Show the help functionality for the command                                                                                                                                                                                               | Optional             |

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
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=${env.PWD} \
  --env HELM_CONFIG_HOME=${env.PWD} \
  --volume ${PWD}/<DEPENDENCY_CACHE_DIRECTORY>:/<DEPENDENCY_CACHE_DIRECTORY> \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  helmfile_executor get-release-details-from-helmfile \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file <SITE_VALUES_FILE> \
  --get-all-images <NUMBER_OF_DAYS> \
  --fetch-charts <BOOLEAN_TRUE_OR_FALSE> \
  --chart-cache-repository ${PWD}/<PATH_TO_DEPENDENCY_CACHE_DIRECTORY> \
  --helmfile-url <FULL_HELMFILE_URL>
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
