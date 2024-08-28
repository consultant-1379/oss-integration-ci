# Check Eric Product Info Images

[TOC]

## Introduction
Writes all image information of images found within the eric-product-info.yaml files gathered from the chart and sub-charts/microservices to a json file.

## Prerequisites
The following is a list of required prerequisites
- A clone of the chart repository with the changes/TGZ File of the chart you want to test against.

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor check-eric-product-info-images --help
```

### Executing the command
The following is an example of running the command:

```
docker run \
  --init --rm \
  --user $(id -u):$(id -g) \
  --volume $PWD:/ci-scripts/output-files \
  --volume $PWD:$PWD \
  --workdir $PWD \
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> \
  pre_code_review_executor check-eric-product-info-images \
  --chart-full-path $PWD/<CHART_FULL_PATH>
```

### Available Parameters
| Parameter         | Description                                                                                       | Optional or Required |
|-------------------|---------------------------------------------------------------------------------------------------|----------------------|
| --chart-full-path | The path to the directory that contains the Chart.yaml that is stored within the Chart directory. | Required             |
| --verbosity       | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                            | Optional             |
| --help            | Show the help functionality for the command                                                       | Optional             |

### Output
A json file that contains the collected images from the eric-product-info.yaml called image_information_list.json that is returned.

See example output below:
```
{
    "eric-oss-pm-stats-calc-handling": [
        {
            "eric-api-gateway-client": "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-api-gateway-client:1.0.59-1"
        },
        {
            "keycloak-client": "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client:1.3.0-1"
        },
        {
            "eric-sef-exposure-api-manager-client": "armdocker.rnd.ericsson.se/proj-adp-rs-sef-released/eric-sef-exposure-api-manager-client:3.6.0-153"
        },
    ]
}
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