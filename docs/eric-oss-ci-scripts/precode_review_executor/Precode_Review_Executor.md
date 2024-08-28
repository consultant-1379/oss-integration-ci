## Precode Review Executor

[TOC]

## Introduction
This is the main executor for the commands used within Precode Review Jobs for Applications/Helmfiles.

The functionality available within the Precode Review Executor ensure that the Application/Helmfile specified adheres to the tests specified.

The commands available for use through this executor are listed below.

## Execute "pre_code_review_executor" help
To execute a command for the executor the following are the basic volumes and details needed,
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> pre_code_review_executor --help
```

## Available commands
| Command                                             | Description                                                                                                | Link                                                                                                             |
|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| add_experimental_permissions_for_docker_config_file | Add experimental permissions to docker config file in order to check eric-product-info images.             | [Add_Experimental_Permissions_For_Docker_Config_File.md](Add_Experimental_Permissions_For_Docker_Config_File.md) |
| check_eric_product_info_images                      | Collect images from the eric-product-info.yaml file of the chart & subcharts and ensures the images exist. | [Check_Eric_Product_Info_Images.md](Check_Eric_Product_Info_Images.md)                                           |
| helm_lint                                           | Execute the Helm lint against a given helm chart.                                                          | [Helm_Lint.md](Helm_Lint.md)                                                                                     |
| helmfile_static_tests                               | Execute the Helmfile Static Tests against a given helmfile.                                                | [Helmfile_Static_Tests.md](Helmfile_Static_Tests.md)                                                             |
| static_tests                                        | Execute the Static Tests against a given helm chart.                                                       | [Static_Tests.md](Static_Tests.md)                                                                               |
| schema_tests                                        | Execute the Schema Tests against a given helm chart.                                                       | [Schema_Tests.md](Schema_Tests.md)                                                                               |
| yaml_lint_application_chart                         | Performs yamllint against an application chart given a yamllint configuration file.                        | [Yaml_Lint_Application_Chart.md](Yaml_Lint_Application_Chart.md)                                                 |
| yaml_lint_helmfile                                  | Performs yamllint against an helmfile given a yamllint configuration file.                                 | [Yaml_Lint_Helmfile.md](Yaml_Lint_Helmfile.md)                                                                   |
| validate_chart_against_schema_file_tests            | Execute the schema validation against a given helm chart.                                                  | [Validate_Chart_Against_Schema_File.md](Validate_Chart_Against_Schema_File.md)                                   |

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