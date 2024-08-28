# Populating the Object Store Tool (OST) with Environment Files details

[TOC]

## Introduction

This document describes the process on populating the files for an environment into the OST for use with the OSS
Integration CI Flows.
  > There is more info on OST itself under this link, [https://atvost.athtem.eei.ericsson.se/](https://atvost.athtem.eei.ericsson.se/).
  >
> Ticketmaster is not responsible for the workings of OST.

## Overview

Prior to the introduction of OST, the environment files were stored in the Jenkins credentials. This was sometimes
cumbersome for teams to keep updated.

With the introduction of OST it is a more user-friendly interface, for the user to be able to edit environment file(s)
details.

All the environment files details are stored in OST, These files can be mapped to multiple deployment Documents, see
more on deployment document creation [here](DIT_Deployment_Generation.md)
The details stored in OST for environment files are used currently in the following Jenkins files,
[Helmfile Deploy using DIT](Helmfile_Deploy_Using_DIT.md), [Gather Environment Details using DIT](gatherEnvDetailsUsingDIT.md),
[Purge Environment using OST](purgeUsingOST.md) etc.

### Structure

Environment file information is stored in OST under ["Buckets"](https://atvost.athtem.eei.ericsson.se/buckets).
All buckets listed in this view is what the user has access to/owns.

Please see the following page for a naming convention when generating a new Files Bucket,
[Naming Convention for OST Bucket](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=DGBase&title=AETB-254+Investigate+naming+convention+for+this+storage+solution#AETB254Investigatenamingconventionforthisstoragesolution-OST)

### Add a New Environment Files Bucket
To add a new environment files bucket, execute the following steps.

1. Open up the ["Buckets"](https://atvost.athtem.eei.ericsson.se/buckets). in OST
2. Click on the ***Create new Bucket*** button.
3. Enter the name of the Bucket, following the document, [Naming Convention for OST Bucket](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=DGBase&title=AETB-254+Investigate+naming+convention+for+this+storage+solution#AETB254Investigatenamingconventionforthisstoragesolution-OST)
   > Please take note of the Bucket name as it will be needed in the Environment Document in DIT, see [here](DIT_Deployment_Generation.md)
4. Choose the appropriate Privacy Policy. (Private, only the users listed can view/configure, Public everyone can access and configure)
5. Add the user(s) that should have access to edit/add files to the Bucket. (Note: Users need to have logged into OST at
least once to appear on the dropdown.)
6. Save.

A new Bucket should be created. Enter the Bucket and add the files using the "Create Data-File", following the
instruction on screen. Note the only file currently needed is the Kube_config.yaml file used to log into the kubernetes
environment. **NOTE** Ensure the Kube config file has the correct API key so that it can be accessed external
to the Director.

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
