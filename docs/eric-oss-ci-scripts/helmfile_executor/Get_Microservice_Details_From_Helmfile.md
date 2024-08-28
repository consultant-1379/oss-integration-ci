# Get Microservice Details From Helmfile

[TOC]

## Introduction
The command is used to write all the microservice dependency details within a helmfile to a JSON file.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor get-microservice-details-from-helmfile --help
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
  helmfile_executor get-microservice-details-from-helmfile \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION> \
  --state-values-file ${PWD}/<SITE_VALUES_FILE>
```


### Available Parameters
| Parameter               | Description                                                               | Optional or Required |
|-------------------------|---------------------------------------------------------------------------|----------------------|
| --path-to-helmfile      | This is the full path to the helmfile under test, including the file name | Required             |
| --state-values-file     | The full path to the site-values file used to template the helmfile       | Required             |
| --verbosity             | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)    | Optional             |
| --help                  | Show the help functionality for the command                               | Optional             |

### Output
A pair of JSON output files will be created named helmfile_services_json_content.json and helmfile_shared_services_json_content.json.
The first contains details of each of the microservices contained within the helmfile including location, product name and number,
repo URL and version. While the second lists the number of times each microservice is shared across all charts.

Listed below is an excerpt of an example of each:

```
{
    "eric-aiml-model-lcm-crd": {
        "eric-aiml-model-lcm-crd": {
            "location": "./eric-aiml-model-lcm-crd/",
            "product_number": "CXD 101 390",
            "version": "0.3.0+68"
        }
    },
    "eric-cloud-native-base": {
        "eric-cloud-native-base": {
            "location": "./eric-cloud-native-base/",
            "product_number": "CXD 101 001",
            "version": "123.1.0-EP2"
        },
        "eric-cloud-native-kvdb-rd-operand": {
            "location": "./eric-cloud-native-base/charts/eric-cloud-native-kvdb-rd-operand",
            "product_number": "CXD 101 001",
            "version": "4.12.0+4"
        },
        "eric-cm-mediator": {
            "location": "./eric-cloud-native-base/charts/eric-cm-mediator",
            "product_number": "CXC 201 1506",
            "version": "8.11.0+29"
        },
        "eric-ctrl-bro": {
            "location": "./eric-cloud-native-base/charts/eric-ctrl-bro",
            "product_number": "CXC 201 2182",
            "version": "8.3.0+31"
        },
        "eric-data-coordinator-zk": {
            "location": "./eric-cloud-native-base/charts/eric-data-coordinator-zk",
            "product_number": "CXC 201 1474",
            "version": "2.1.0+18"
        },
        "eric-data-distributed-coordinator-ed": {
            "location": "./eric-cloud-native-base/charts/eric-data-distributed-coordinator-ed",
            "product_number": "CXC 201 2039",
            "version": "9.1.0+16"
        }
    }
}
```

```
{
    "eric-data-document-database-pg": 10,
    "eric-eo-credential-manager": 2,
    "eric-eo-subsystem-management": 2,
    "eric-eo-subsystemsmgmt-ui": 2,
    "eric-lcm-smart-helm-hooks": 2,
    "eric-log-shipper": 8
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
