# Get CRD Details From Chart

[TOC]

## Introduction
This command is used to retrieve CRD details from a chart and generate a new property file with chart details.

## Prerequisites
The following is a list of required prerequisites
- A downloaded and untarred Helmfile which is built to retrieve CSAR details
- Artifactory credentials for fetching the chart from Artifactory - which can be provided as arguments, or environment variables. See examples below
- An adp-crd-handler docker image e.g. armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:latest
- Run the container with root permissions i.e., --user 0:0

## How to use the Docker image
The docker image, "eric-oss-ci-scripts" is built intermittently.
To ensure the latest version of the image is being used, please see the labels on the oss-integration-ci
repo for the latest available version.

Each label represents a version of the eric-oss-ci-scripts docker image.

To execute the command the following are the basic volumes and details needed,
```
docker run \
  --init --rm \
  --user 0:0 \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume <PATH>/.docker:/root/.docker \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> crd_executor get-crd-details-from-chart --help
 ```

### Executing the command
The following is an example of running the command.
Note the use of the username and password arguments, as opposed to environment variables.
```
docker run \
  --init --rm \
  --user 0:0 \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume <PATH>/.docker:/root/.docker \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  crd_executor get-crd-details-from-chart \
  --path-to-helmfile <PATH TO HELMFILE> \
  --chart-name <CHART NAME> \
  --chart-version <CHART VERSION> \
  --chart-repo <CHART REPO> \
  --image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:<VERSION> \
  --username <USERNAME> \
  --password <PASSWORD>
```


### Available Parameters
| Parameter          | Description                                                                                                                                                                                           | Optional or Required       |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| --path-to-helmfile | The path to the helmfile that will be built to retrieve CRD details.                                                                                                                                  | Required                   |
| --chart-name       | The name of the chart to check for CRDs.                                                                                                                                                              | Required                   |
| --chart-version    | The version of the chart to check for CRDs.                                                                                                                                                           | Required                   |
| --chart-repo       | The repository url of the chart to check for CRDs.                                                                                                                                                    | Required                   |
| --image            | The adp-crd-handler image to use.                                                                                                                                                                     | Required                   |
| --username         | This is the username to log into Artifactory. This can also be set as an environment variable. Optional, because credentials can be passed using this argument or an environment variable. See below. | Optional (See description) |
| --password         | This is the password to log into Artifactory. This can also be set as an environment variable. Optional, because credentials can be passed using this argument or an environment variable.See below.  | Optional (See description) |
| --verbosity        | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                | Optional                   |
| --help             | Show the help functionality for the command                                                                                                                                                           | Optional                   |

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

If adding these parameters as environment variables, extra config is required on the docker run command to pass the
environment variables i.e. "--env <VARIABLE>" to the docker image during execution.

See example below
```
docker run \
  --init --rm \
  --user 0:0 \
  --env GERRIT_USERNAME \
  --env GERRIT_PASSWORD \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume <PATH>/.docker:/root/.docker \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  crd_executor get-crd-details-from-chart \
  --path-to-helmfile <PATH TO HELMFILE> \
  --chart-name <CHART NAME> \
  --chart-version <CHART VERSION> \
  --chart-repo <CHART REPO> \
  --image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:<VERSION>
```

### Output
A properties file called crd_details_artifact.properties is returned.

See example output below:
```
CHART_NAME=eric-cloud-native-base, eric-data-key-value-database-rd-crd, eric-sec-access-mgmt-crd, eric-sec-certm-crd, eric-sec-sip-tls-crd, eric-tm-ingress-controller-cr-crd
CHART_VERSION=158.1.0, 2.0.0+5, 1.1.0+1, 5.0.0+18, 6.1.0+1, 11.3.0+59
CHART_REPO=https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm
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
