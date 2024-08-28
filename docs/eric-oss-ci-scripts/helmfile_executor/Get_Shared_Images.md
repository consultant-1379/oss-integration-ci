# Get Shared Images

[TOC]

## Introduction
The command is used to get all the images shared between charts within a helmfile and output them to a JSON file.

## Prerequisites
The following is a list of require prerequisites
- Helmfile tar file
- Functional User credentials to access any docker repositories

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
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor get-shared-images --help
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
  helmfile_executor get-shared-images \
  --path-to-helmfile $PWD/<HELMFILE_YAML_LOCATION> \
  --username <FUNCTIONAL_USER_USERNAME> \
  --user-password <FUNCTIONAL_USER_PASSWORD>
```


### Available Parameters
| Parameter          | Description                                                                                                                                                                                                                               | Optional or Required |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| --path-to-helmfile | This is the full path to the helmfile under test, including the file name.                                                                                                                                                                | Required             |
| --username         | This is the username to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable      | Required             |
| --user-password    | This is the user password to log into Artifactory. This can also be set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed. See "Hiding Sensitive Information" below on how to set an environment variable | Required             |
| --verbosity        | Used to set the log level verbosity, 0 lowest, 4 highest  (default: 3)                                                                                                                                                                    | Optional             |
| --help             | Show the help functionality for the command                                                                                                                                                                                               | Optional             |

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
  helmfile_executor get-shared-images \
  --path-to-helmfile ${PWD}/<HELMFILE_YAML_LOCATION>
```

### Output
A pair of JSON output files will be created named helmfile_shared_images.json and outdated_images_per_chart.json.

The information contained in the first file, helmfile_shared_images.json, includes the number of occurrences of each
image and each individual version's frequency along with the sources of each occurrence. An example of the content is
shown below:

```
{
    "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client": {
        "Number of occurrences": 17,
        "Different versions and frequency": {
            "1.0.0-102": 12,
            "1.0.0-100": 3,
            "1.0.0-88": 1,
            "1.0.0-99": 1
        },
        "Sources of occurrences": {
            "eric-eiae-helmfile/charts/eric-eic-common-base-config": "1.0.0-102",
            "eric-cnbase-oss-config": "1.0.0-102",
            "eric-cncs-oss-config": "1.0.0-102",
            "eric-oss-common-base": "1.0.0-100",
            "eric-oss-common-base/charts/eric-gr-bur-orchestrator": "1.0.0-100",
            "eric-oss-common-base/charts/eric-eo-api-gateway": "1.0.0-102",
            "eric-oss-common-base/charts/eric-oss-key-management-agent": "1.0.0-102",
            "eric-oss-common-base/charts/eric-eo-subsystem-management": "1.0.0-102",
            "eric-oss-common-base/charts/eric-eo-usermgmt": "1.0.0-100",
            "eric-oss-oran-support/charts/eric-oss-a1-policy-mngmt-svc": "1.0.0-102",
            "eric-oss-dmm": "1.0.0-102",
            "eric-topology-handling/charts/eric-oss-common-topology-svc/charts/eric-oss-cmn-topology-svc-core": "1.0.0-88",
            "eric-oss-ericsson-adaptation/charts/eric-oss-ran-topology-adapter": "1.0.0-102",
            "eric-oss-app-mgr": "1.0.0-102",
            "eric-oss-config-handling/charts/eric-oss-ncmp": "1.0.0-102",
            "eric-oss-pm-stats-calc-handling": "1.0.0-99",
            "eric-oss-connected-systems-registry/charts/eric-eo-subsystem-management": "1.0.0-102"
        }
    },
    "armdocker.rnd.ericsson.se/proj-document-database-pg-release/data/eric-data-document-database-pg13": {
        "Number of occurrences": 14,
        "Different versions and frequency": {
            "8.14.0-50": 10,
            "8.13.0-47": 4
        },
        "Sources of occurrences": {
            "eric-cloud-native-base/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-oss-common-base/charts/eric-data-document-database-pg": "8.13.0-47",
            "eric-oss-dmm": "8.14.0-50",
            "eric-oss-dmm/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-topology-handling/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-oss-ericsson-adaptation/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-oss-app-mgr/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-oss-config-handling/charts/eric-data-document-database-pg": "8.13.0-47",
            "eric-oss-pm-stats-calc-handling/charts/eric-oss-pm-stats-calculator": "8.14.0-50",
            "eric-oss-pm-stats-calc-handling/charts/eric-oss-pm-stats-calculator/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-oss-ml-execution-env": "8.14.0-50",
            "eric-oss-ml-execution-env/charts/eric-data-document-database-pg": "8.14.0-50",
            "eric-top-inv-exposure-handling/charts/eric-oss-top-inv-exposure": "8.13.0-47",
            "eric-oss-connected-systems-registry/charts/eric-data-document-database-pg": "8.13.0-47"
        }
    }
}
```

The second generated file, outdated_images_per_chart.json, contains details of any charts with outdated images along
with the current version in the chart and latest one in the corresponding docker repository. An example of the content
is shown below:

```
{
    "eric-oss-common-base": {
        "keycloak-client": {
            "Repo": "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client",
            "Current version": "1.0.0-100",
            "Latest version": "1.0.0-102"
        },
        "charts": {
            "eric-gr-bur-orchestrator": {
                "keycloak-client": {
                    "Repo": "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client",
                    "Current version": "1.0.0-100",
                    "Latest version": "1.0.0-102"
                }
            },
            "eric-eo-usermgmt": {
                "keycloak-client": {
                    "Repo": "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client",
                    "Current version": "1.0.0-100",
                    "Latest version": "1.0.0-102"
                }
            },
            "eric-data-document-database-pg": {
                "eric-data-document-database-pg13": {
                    "Repo": "armdocker.rnd.ericsson.se/proj-document-database-pg-release/data/eric-data-document-database-pg13",
                    "Current version": "8.13.0-47",
                    "Latest version": "8.14.0-50"
                },
                "eric-data-document-database-kube-client": {
                    "Repo": "armdocker.rnd.ericsson.se/proj-document-database-pg-release/data/eric-data-document-database-kube-client",
                    "Current version": "8.13.0-47",
                    "Latest version": "8.14.0-50"
                },
                "eric-data-document-database-metrics": {
                    "Repo": "armdocker.rnd.ericsson.se/proj-document-database-pg-release/data/eric-data-document-database-metrics",
                    "Current version": "8.13.0-47",
                    "Latest version": "8.14.0-50"
                }
            }
        }
    }
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
