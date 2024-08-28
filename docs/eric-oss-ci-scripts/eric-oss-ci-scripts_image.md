# CI/CD Docker Image.

[TOC]

## Introduction
In modern software development and deployment, Docker has revolutionised the way we package, distribute,
and execute applications. At its core, a Docker image is a lightweight, standalone, and executable package that contains
all the necessary components and dependencies to run an application.
This encapsulation includes the application code, runtime environment, libraries, and tools, ensuring consistency and
portability across different environments.

Within our Continuous Integration (CI) pipeline, particularly in Jenkins, Docker images play a pivotal role in
streamlining our deployment processes. By leveraging Docker images, we can encapsulate a predefined set of components
and tools required for our CI workflow. This not only simplifies the setup and configuration but also enhances
reproducibility and scalability across various stages of our CI pipeline.

### Usage within Ticketmaster CI Jenkins File

In the Ticketmaster CI Jenkins File, we integrate this Docker image to execute commands seamlessly.
This Docker images is pre-configured with essential components such as Helm, Helmfile, Kubernetes, and other
dependencies, ensuring that our environment is consistent and ready to execute our deployment steps.

Currently, the image is heavily used with the Ticketmaster CI Jenkins jobs, but the commands can also be executed standalone.
Please see more info on the available commands below.

## How to use the Docker image
The docker image, "eric-oss-ci-scripts" is built intermittently.
To ensure the latest version of the image is being used, please see the labels/tags on the [oss-integration-ci
repo](https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS%2Fcom.ericsson.oss.aeonic%2Foss-integration-ci.git;a=shortlog;h=refs%2Fheads%2Fmaster) for the latest available version.

Each label represents a version of the eric-oss-ci-scripts docker image.

To see the help of docker image, execute
```
docker run
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> --help
 ```
 To see the info about the available commands within the Image execute the help against the command
```
docker run
  armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> <COMMAND> --help
 ```

## Available commands
| Command                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Link                                                                          |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| cihelm_executor          | This executor can be used to<br/> - fetch helmfile dependencies<br/> - package a give helm chart and its dependencies<br/> - download a single helm chart from a repo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | [cihelm_executor](cihelm_executor/CI-Helm_Executor.md)                        |
| confluence_executor      | This executor can be used to<br/> - copy documents stored in a gerrit repo to confluence<br/> - create Jira tickets for charts with outdated images                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | [confluence_executor](confluence_executor/Confluence_Executor.md)             |
| crd_executor             | This executor can be used to<br/> - validate CRD manifests from a specified directory using Kubeconform<br/> - retrieve CRD details from a chart and generate a new property file with chart details<br/> - delete CRD components<br/> - update releases in the crds-helmfile with 'installed: true', where the installation of the release is dependent on certain 'tags'                                                                                                                                                                                                                                                                                                                                                | [crd_executor](crd_executor/CRD_Executor.md)                                  |
| csar_executor            | This executor can be used to<br/> - check for CSARs in a given repo<br/> - download CSARs<br/> - check the images in a CSAR                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | [csar_executor](csar_executor/CSAR_Executor.md)                               |
| gerrit_executor          | This executor can be used to<br/> - create a Gerrit patch<br/> - check if a Gerrit patch is submittable                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | [gerrit_executor](gerrit_executor/Gerrit_Executor.md)                         |
| helm_chart_executor      | This executor can be used to<br/> - get chart names and versions from a helm chart<br/> - package a chart into a versioned chart archive file<br/> - remove releases from a specified namespace<br/> - remove Storage Encryption Provider from specified namespace<br/> - compare microservice versions from a chart to the latest versions in the relevant repo<br\> -assess that all optionality CNCS values are contained within the dependencies in the Chart.yaml files                                                                                                                                                                                                                                              | [helm_chart_executor](helm_chart_executor/Helm_Chart_Executor.md)             |
| helmfile_executor        | This executor can be used to<br/> - get chart names and versions from a helmfile<br/> - download a helmfile from artifactory<br/> - get details about CSARs to be created<br/> - verify existing releases against expected releases<br/> - get microservice dependency details<br/> - compare application versions between a helmfile with the latest versions in the associated repo<br/> - get the latest helmfile version from a repo<br/> - get application names and versions from a helmfile<br/> - get the images shared between charts<br/> - update a repository yaml file with credentials<br/> - generate an optionality maximum yaml file<br/> - check chart versions in a helmfile against versions provided | [helmfile_executor](helmfile_executor/Helmfile_Executor.md)                   |
| kubectl_executor         | This executor can be used to<br/> - perform various Kubernetes Commands on a target cluster <br/> - create a namespace<br/> - delete a namespace<br/> - creation and removal of resources (Namespace Secret, Internal Registry Secret, ClusterRolebindings, Rolebindings, Service Accounts) on a specified namespace<br/> - wait for Persistent Volume Deletion<br/> - wait for UDS Backend Job to complete<br> - get data from secret or configmap                                                                                                                                                                                                                                                                       | [kubectl_executor](kubectl_executor/Kubectl_Executor.md)                      |
| pre_code_review_executor | This executor can be used to<br/> - replicate stages used within the Application & Helmfile Precode Review Jobs<br/> - perform helmfile and application static tests<br/> - perform helm lint tests<br/> - perform shell checks<br/> - gather all images from the eric-product-info.yaml from charts and sub-charts to run manifest inspect commands to ensure that the image exists on the registry.                                                                                                                                                                                                                                                                                                                     | [precode_review_executor](precode_review_executor/Precode_Review_Executor.md) |
| site_values_executor     | This executor can be used to<br/> - create a new site-values file using a list of keys and values<br/> - update a site values file by enabling a list of tags<br/> - merge a base yaml file with an override yaml file<br/> - obfuscate a cleartext registry password within a site-values file<br/> - set selected deployment tags in a site-values file<br/> - substitute placeholder variables in a site-values file with new ones                                                                                                                                                                                                                                                                                     | [site_values_executor](site_values_executor/Site_Values_Executor.md)          |
| utils_executor           | This executor can be used to<br/> - clean the workspace from details in a property file using AM package manager (Internal Only)<br/> - convert a yaml file to a json file for further processing<br/> - extract a given tar file<br/> - get the Deployment Manager (DM) tag from the file inputted and output to the properties file given                                                                                                                                                                                                                                                                                                                                                                               | [utils_executor](utils_executor/Utils_Executor.md)                            |


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
