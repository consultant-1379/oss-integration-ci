## Helmfile Executor

[TOC]

## Introduction
This is the main executor for Helmfile commands.

A Helmfile is a declarative spec used for deploying helm charts via Kubernetes. This executor provides functionality
related to Helmfiles. This ranges from downloading a specific Helmfile version from artifactory to getting the images
shared between charts within the Helmfile and checking the releases within a deployed Helmfile.

## Execute "helmfile_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> helmfile_executor --help
```

## Available commands
| Command                                        | Description                                                                                           | Link                                                                                                   |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| check-helmfile-deployment                      | Checks all existing releases against expected releases within a deployment                            | [Check_Helmfile_Deployment.md](Check_Helmfile_Deployment.md)                                           |
| check-helmfile-versions-against-given-versions | Checks the chart versions within a helmfile against a list of versions provided                       | [Check_Helmfile_Versions_Against_Given_Versions.md](Check_Helmfile_Versions_Against_Given_Versions.md) |
| compare-application-versions-from-helmfile     | Compares the application versions within the helmfile to the latest versions within the relevant repo | [Compare_Application_Versions_From_Helmfile.md](Compare_Application_Versions_From_Helmfile.md)         |
| download-helmfile                              | Downloads a specific helmfile version from a designated repository                                    | [Download_Helmfile.md](Download_Helmfile.md)                                                           |
| generate-optionality-maximum                   | Creates an optionality maximum yaml file                                                              | [Generate_Optionality_Maximum.md](Generate_Optionality_Maximum.md)                                     |
| get-app-version-from-helmfile                  | Gets all chart names and their versions from a helmfile                                               | [Get_App_Version_From_Helmfile.md](Get_App_Version_From_Helmfile.md)                                   |
| get-base-baseline                              | Gets all application names and their associated versions listed in the helmfile                       | [Get_Base_Baseline.md](Get_Base_Baseline.md)                                                           |
| get-latest-helmfile-version                    | Downloads the most recent version of a given helmfile from the specified repo                         | [Get_Latest_Helmfile_Version.md](Get_Latest_Helmfile_Version.md)                                       |
| get-microservice-details-from-helmfile         | Gets all details of the microservice dependency information within the helmfile                       | [Get_Microservice_Details_From_Helmfile.md](Get_Microservice_Details_From_Helmfile.md)                 |
| get-release-details-from-helmfile              | Writes several files to describe CSAR build and releases from a helmfile                              | [Get_Release_Details_From_Helmfile.md](Get_Release_Details_From_Helmfile.md)                           |
| get-shared-images                              | Gets the images shared between each chart of a helmfile                                               | [Get_Shared_Images.md](Get_Shared_Images.md)                                                           |
| populate-repository-credentials                | Populates the repository yaml file with provided credentials                                          | [Populate_Repository_Credentials.md](Populate_Repository_Credentials.md)                               |

## Contacts

### Guardians

See in [Contributing Guide](../Contribution_Guide.md)

### Backlog

Create a new issue on Ticketmaster component under ADPPRG project:

Report [Support/Bug](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)

See in [Contributing Guide](../Contribution_Guide.md) for further details

### Support

Support is available on our Teams channel:

- Send questions via
  [Ticketmaster - General](https://teams.microsoft.com/l/channel/19%3a9f5ed758e3a6405daffee42e0284268b%40thread.skype/General?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f)
  Microsoft Teams channel
