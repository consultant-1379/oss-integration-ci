# Generate a Gerrit Patch

[TOC]

## Introduction
This command is used to generate a Gerrit patch set based on changes made to a file in a local directory.

## Prerequisites
The following is a list of required prerequisites
- Gerrit User Credentials, this is used to access the repository containing the CSARs
- A cloned Gerrit repository with changes made to the repository
- Access to download the ADP image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:latest

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> gerrit_executor generate-gerrit-patch --help
 ```

### Executing the command
The following is an example of running of the command
- Be inside the Gerrit repository where the changes have been made
- Execute the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  gerrit_executor generate-gerrit-patch \
  --username <USERNAME> \
  --password <PASSWORD> \
  --image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:<VERSION> \
  --message <GERRIT_COMMIT_MESSAGE> \
  --gerrit-repo-local <PATH_TO_GERRIT_REPO> \
  --gerrit-branch <GERRIT_BRANCH>
```


### Available Parameters
| Parameter           | Description                                                                                                                                                                                                                  | Optional or Required |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --username          | This is the username to log into Gerrit. This can also be set as an environment variable, GERRIT_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable.      | Required             |
| --password          | This is the user password to log into Gerrit. This can also be set as an environment variable, GERRIT_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable. | Required             |
| --image             | The ADP image used to create the patch (e.g., armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:latest)                                                                                                      | Required             |
| --message           | The Gerrit commit message                                                                                                                                                                                                    | Required             |
| --gerrit-repo-local | The path to the local Gerrit repository where the changes have been made                                                                                                                                                     | Required             |
| --gerrit-branch     | The Gerrit branch to push the changes to                                                                                                                                                                                     | Required             |
| --verbosity         | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                       | Optional             |
| --help              | Show the help functionality for the command                                                                                                                                                                                  | Optional             |

## Hiding Sensitive Information
Sometimes it maybe necessary to ensure sensitive information is not displayed in a console. This can be achieved with
the use of environment variables.

### Set an Environment variable.
The environment variable should be set prior to the executing of the docker image and in the same shell.

To set an environment variable, execute the export command
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

### Executing the command
The following is an example of running the command
- Have the properties file containing the CSAR names and versions
- Execute the command
```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --env GERRIT_USERNAME \
  --env GERRIT_PASSWORD \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  gerrit_executor generate-gerrit-patch \
  --image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:<VERSION> \
  --message <GERRIT_COMMIT_MESSAGE> \
  --gerrit-repo-local <PATH_TO_GERRIT_REPO> \
  --gerrit-branch <GERRIT_BRANCH>
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
