# Populating the Deployment Inventory Tool (DIT) with Environment details

[TOC]

## Introduction

This document describes the process on populating a deployment into the DIT for use with the OSS Integration CI Flows.
  > There is more info on DIT itself under this link, [https://atvdit.athtem.eei.ericsson.se/](https://atvdit.athtem.eei.ericsson.se/).
  >
> Ticketmaster is not responsible for the workings of DIT.

> Note: The following needs to be in place before proceeding with the addition of a new Environment document.
>
> - Ensure the certificates have been stored in OST in the environment certificates bucket,
> see [here](OST_Deployment_Certificates_Bucket_Generation.md) for details
> - Ensure the environment associated files have been stored in OST in the files bucket for the environment,
> see [here](OST_Deployment_Files_Bucket_Generation.md) for details

## Overview

Prior to the introduction of DIT, the environment configuration files were stored in GIT. This was sometimes
cumbersome for teams to keep updated. Also, it was time-consuming to add new entries to the config file and update the CI
scripts accordingly.

With the introduction of DIT it is a more user-friendly interface, for the user to be able to edit deployment details.
It gives flexibility to teams to be able to add extra keys to the environment details, which can be picked up
automatically and populated into the site values file, as long as the key exists, within either the site values template
or the override file.

All the environment specific details are stored in DIT and is the main page for all the environment details.
The details stored in DIT are used in a number of Jenkins files i.e. [Gather Environment Details using DIT](gatherEnvDetailsUsingDIT.md),
[Helmfile Deploy using DIT](Helmfile_Deploy_Using_DIT.md) etc.

### Structure

Environment information is stored in DIT under ["Other Documents sections"](https://atvdit.athtem.eei.ericsson.se/documents/list/other).
It uses a schema to generate the layout of the Document.

Ticketmaster currently have a default schema that can be used to generate their environment document. This schema file
will have all the default values that is needed by the main site values template.

Ticketmaster are responsible for keeping the latest site values template updated with new required values.
During this proces ticketmaster will also ensure the schema is kept updated to match the latest site values.
The schema can be seen here, [DIT Schemas](https://atvdit.athtem.eei.ericsson.se/schemas) search for
 - "EIC_TICKETMASTER_default_test_environment_schema" for EIC schema.
 - "EO_TICKETMASTER_default_test_environment_schema" for EO schema.

If a team needs to add extra values to the environment i.e. they may want to swap a value out of their override file
that is not currently under the default schema, they may need to create their own schema file. Ensure to use the
Ticketmaster default schema as the base of the new schema file. It will be the responsibility of the team going forward
to ensure that file is kept updated.

If a number of teams need the same value set, then please register a
[support ticket](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091) on Ticketmaster to analyse the
request to see can it be added to the default schema.

Please see the following page for a naming convention when generating a new environment Documents,
[Naming Convention for DIT](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/AETB-254+Investigate+naming+convention+for+this+storage+solution#AETB254Investigatenamingconventionforthisstoragesolution-DIT)

An example document owned by Ticketmaster can be seen here for EIC Project, [hart105_OSS_DEPLOY](https://atvdit.athtem.eei.ericsson.se/documents/view/63b45cb82792fdf7c33a46ed)
and one here for EO Project, [hart105_EO_OSS_DEPLOY](https://atvdit.athtem.eei.ericsson.se/documents/view/64945d32eb9881d1c0c64d2e)

### Add a New Document
Before a new document is added, please take note of a few of the main parameters needed.
There maybe other parameters needed also, please see the latest schema for details.

| Parameter                    | Description                                                                                                                                                                                                      | Default          |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| PLATFORM                     | This is used to describe the platform, being executed on KaaS, Azure, AWS, GCP, CCD, EWS, etc. This is used within the helmfile deploy jenkins job to execute certain stages depending on the PLATFORM specified |                  |
| NAMESPACE                    | This is the main namespace the deployment will be executed onto, it defaults to, oss-deploy                                                                                                                      | oss-deploy       |
| CRD_NAMESPACE                | This is the CRD namespace the deployment will be executed onto, it default to, eric-crd-ns                                                                                                                       | eric-crd-ns      |
| ENV_CERTIFICATES_BUCKET_NAME | This is the bucket name in the Object Storage Tool (OST), that is storing the certificates for the environment, see [here](OST_Deployment_Certificates_Bucket_Generation.md) for details                         |                  |
| ENV_FILES_BUCKET_NAME        | This is the bucket name in the Object Storage Tool (OST) that stores the files associated with the environment, e.g kubernetes config file, see [here](OST_Deployment_Files_Bucket_Generation.md) for details    |                  |
| KUBE_CONFIG                  | This is the name of the kubernetes Config file that is stored in environment file bucket (ENV_FILES_BUCKET_NAME), this name should include the file extension, defaults to kube_config.yaml                      | kube_config.yaml |
| XYZ_HOST_REPLACE             | There are a number of Host Replace parameters and they are associated to a host within the site values file. Enter the Hostname associated to this parameter or defaults to none                                 | none             |
| IPV6_ENABLE_REPLACE          | This is used to enable IPv6 support. Set to either true or false.                                                                                                                                                |                  |
| XYZ_IP_REPLACE               | There is a number of references to IP Replace these are all looking for a public routeable IP, i.e. ingress ip. These must be a valid ipv4 address or defaults to none                                           | none             |
| DDP_XYZ                      | There are a number of DDP details needed from ID, ACCOUNT and password.                                                                                                                                          | none             |
| ENM_XYZ                      | There are a number of ENM details needed from HOSTNAME, PORT, Scripting IP and Scripting PORT                                                                                                                    | none             |
To add a new environment document to hold the environment details, execute the following steps.

1. Open up the ["Other Documents section"](https://atvdit.athtem.eei.ericsson.se/documents/list/other) in DIT
2. Click on the ***create new document*** button.
3. Enter the name of the document, following the document, [Naming Convention for DIT](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/AETB-254+Investigate+naming+convention+for+this+storage+solution#AETB254Investigatenamingconventionforthisstoragesolution-DIT)
4. Choose the Appropriate schema file for your environment either Ticketmaster's latest schema or the team schema file
5. Populate the parameters as appropriate and save.

## Contributing

We are an inner source project and welcome contributions. See our
[Contributing Guide](../Contribution_Guide.md) for details.

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
