# Helmfile Static Tests

[TOC]

## Introduction
This command is used to execute the Static Tests against a given helmfile.

## Prerequisites
The following is a list of required prerequisites
- A clone of the oss-integration-ci repository within the working directory.
- Optionality Maximum file generated from the "Generate Optionality Maximum" stage - Information on how to run this locally can be found on: [Generate Optionality Maximum](https://eteamspace.internal.ericsson.com/display/DGBase/Run+Helmfile+Precode+Stages+Locally+-+Generate+Optionality+Maximum).
- Combined Site Values file generated from the "Generate Site Values" stage - Information on how to run this locally can be found on: [Generate Site Values File](https://eteamspace.internal.ericsson.com/display/DGBase/Run+Helmfile+Precode+Stages+Locally+-+Generate+Site+Values+File).
- Relevant Gerrit user credentials must be set up in order to fetch all dependencies within the Helmfile (GERRIT_USERNAME & GERRIT_PASSWORD).

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
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=$PWD \
  --env HELM_CONFIG_HOME=$PWD \
  --volume $PWD/cachedir/:$PWD/cachedir/ \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor helmfile-static-tests --help
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
  --env HELM_VERSION=3.6.2 \
  --env XDG_DATA_HOME=/helm_data/ \
  --env HELM_CACHE_HOME=$PWD \
  --env HELM_CONFIG_HOME=$PWD \
  --volume $PWD/cachedir/:$PWD/cachedir/ \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  pre_code_review_executor helmfile-static-tests \
  --state-values-file $PWD/<SITE_VALUES_FILE_GENERATED> \
  --helmfile-full-path $PWD/<HELMFILE_PATH> \
  --specific-skip-file $PWD/<SPECIFIC_SKIP_LIST_FILE> \
  --common-skip-file $PWD/<COMMON_SKIP_LIST_FILE> \
  --check_specific_content $PWD/<CHECK_SPECIFIC_CONTENT_FILE_PATH> \
  --username <USERNAME> \
  --password <PASSWORD>
```

### Available Parameters
| Parameter                | Description                                                                                                                                                                                                                                                                        | Optional or Required |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --helmfile-full-path     | The absolute path to the helmfile.yaml that is stored within the Helmfile directory.                                                                                                                                                                                               | Required             |
| --state-values-file      | The absolute path to the site values file that was generated during the "Generate Site Values File" stage.                                                                                                                                                                         | Required             |
| --specific-skip-file     | The absolute path to the helmfile-specific file of static tests to be skipped. This file resides within the oss-integration-ci repository under testsuite/common/helmfile-validator/<helmfile_name>/skip_list.json.                                                                | Required             |
| --common-skip-file       | The absolute path to the file of static tests to be skipped for all Helmfiles. This file resides within the oss-integration-ci repository under testsuite/common/helmfile-validator/common-skip-list.json.                                                                         | Required             |
| --check_specific_content | Full path to the replica check list for the project. This file resides within the oss-integration-ci repository under testsuite/common/helmfile-validator/<helmfile_name>/check_specific_content.json.                                                                             | Required             |
| --username               | This is the username to allow for the dependencies from the helmfile to be fetched via Gerrit. This can also be set as an environment variable, GERRIT_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --password               | This is the user password to allow for the dependencies from the helmfile to be fetched via Gerrit. This can also be set as an environment variable, GERRIT_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --verbosity              | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                                                             | Optional             |
| --help                   | Show the help functionality for the command                                                                                                                                                                                                                                        | Optional             |

## Hiding Sensitive Information
Sometimes it may be necessary to ensure sensitive information is not displayed in a console. This can be achieved with
the use of environment variables.

### Set an Environment variable.
The environment variable should be set prior to the executing of the docker image and in the same shell.

To set and environment variable, execute the export command
```
export COMMAND="true"
```
The above will set "COMMAND" to true for the rest of the shell life. This variable will be available now in the global
environment variables when needed. To see all environment variables execute "env" on the shell.

### Environment Variables Associated to this Command.
The following is a list of global environments variables that can be set prior to executing the command
- export GERRIT_PASSWORD="\<name>"
- export GERRIT_USERNAME="\<password>"

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
  --env GERRIT_PASSWORD \
  --env GERRIT_USERNAME \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  pre_code_review_executor helmfile-static-tests \
  --state-values-file $PWD/<SITE_VALUES_FILE_GENERATED> \
  --helmfile-full-path $PWD/<HELMFILE_PATH> \
  --specific-skip-file $PWD/<SPECIFIC_SKIP_LIST_FILE> \
  --common-skip-file $PWD/<COMMON_SKIP_LIST_FILE>
  --check_specific_content $PWD/<CHECK_SPECIFIC_CONTENT_FILE_PATH> \
```

### Output
A report.html file will be generated within the workspace which showcases what static tests have failed/passed/skipped.

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