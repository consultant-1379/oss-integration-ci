# Credentials used in Jenkins files.

[TOC]

## Introduction

This file explains the different credentials that are used within the Jenkins file, their structure and how they are
added to the Jenkins credentials area.

>> **Note:**
> The user would need to have permission to generate credentials on Jenkins and access to a functional user.
> It is not recommended to use your own credentials in the files. Knowledge of Jenkins admin activities is required.

>> Each area should have their own set of credentials for their flows.

## Overview

Currently, within the Jenkins file these are the different credentials used within the system.
- User Credentials, this is the secret created with the user and password for the functional user.
- Arm Docker User Credentials, this is the docker config file (config.json) with all the docker registries needed.
- Helm Repositories User Credentials, this is the helm credentials (repositories.yaml) to log onto the different repositories.
- Kubernetes Environment Config file, this is the file that is used to interact with the Kubernetes system under test
- ADP DDC SFTP User Credentials, this is the secret created with the user and password for the eric-odca-diagnostic-data-collector-sftp-credentials secret.

## Credential Storage
### User Credentials

This is the username and password of the Functional user set as a secret within the Jenkins Credentials.

Parameter in the Jenkins file which use these credentials, "FUNCTIONAL_USER_SECRET" & "GERRIT_USER_SECRET"

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Username and Password
- Scope Global .....
- Username: <Functional Username>
- Password: <Functional Password>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins)**
- Description: <Description of the added secret>

#### User Token (Optional)

This is the Functional user token to be able to log into Arm repositories.

To obtain this token for a particular user profile,
- Log on as that user to Artifactory
- Click to edit the user profile in the top right corner.
- Enter user password to enable the features on the page.
- Click on the "Generate an Identity Token" button. Enter a description of the token and click Next.

The token is generated. Copy and store the generated token before exiting.

More on Artifactory token management can be seen [here](https://jfrog.com/help/r/jfrog-platform-administration-documentation/introduction-to-the-user-profile)

Parameter in the Jenkins file which use these credentials, "FUNCTIONAL_USER_TOKEN"

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Secret Text
- Secret: <Enter the generated identity token>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins, e.g. ciloopman-arm-token)**
- Description: <Description of the added file>


### Arm Docker Credentials

This is the docker config to allow access to the different arm docker, used when the CI scripts need to pull images
from the docker registry.

Parameter in the Jenkins file which use these credentials, "ARMDOCKER_USER_SECRET"

The docker config.json needs to be created. It is created by logging into the url of the required docker URL, which will
create the config.json automatically. This is usually created in the $HOME/.docker/config.json area or depending on where this has
been configured on your docker system. The docker login can be executed a number of times into different docker registries
each one will be added to the config.json.

``` docker login <URL>```

The following URLs should be logged into and added to the config.json
- armdocker.rnd.ericsson.se
- selndocker.mo.sw.ericsson.se
- serodocker.sero.gic.ericsson.se

Example config.json File

```
{
	"auths": {
		"armdocker.rnd.ericsson.se": {
			"auth": "XXXXXXXXXXYYYYYYYYYYYYYYXXXXXXXXXXXXXXXXX"
		},
		"https://armdockerhub.rnd.ericsson.se": {
			"auth": "XXXXXXXXXXYYYYYYYYYYYYYYXXXXXXXXXXXXXXXXX"
		},
		"selndocker.mo.sw.ericsson.se": {
			"auth": "XXXXXXXXXXYYYYYYYYYYYYYYXXXXXXXXXXXXXXXXX"
		},
		"serodocker.sero.gic.ericsson.se": {
			"auth": "XXXXXXXXXXYYYYYYYYYYYYYYXXXXXXXXXXXXXXXXX"
		}
	},
	"HttpHeaders": {
		"User-Agent": "Docker-Client/17.04.0-ce (linux)"
	}
}
```

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Secret File
- File: <Choose the created config.json from the file system>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins)**
- Description: <Description of the added file>


### Helm Repositories Credentials
This is the helm credentials to log onto the different helm repositories, used when the CI script need to pull artifact
from a helm registry.

Parameter in the Jenkins file which use these credentials, "DOCKER_REGISTRY_CREDENTIALS"

The helm repositories.yaml needs to be created. It is created manually. It doesn't use the password for the functional
user but the Identity Token. To obtain this Key for a particular user profile, log on as that user to Artifactory url
and click to edit the user profile on the top right corner. Enter user password to enable the features on the page.
Next, click on the "Generate an Identity Token" button (DO NOT DELETE A TOKEN UNLESS YOU KNOW THE CONSEQUENCE).
Ensure to SAVE the password from the popup, no way to get it once closed.
Copy the key and add to your repositories.yaml file for that artifactory URL. This may need to be repeated for other
artifactory URLs.

The following URLs should be logged into and added to the config.json
- https://arm.sero.gic.ericsson.se/artifactory/
- https://arm.rnd.ki.sw.ericsson.se/artifactory/ (Redirects to arm.sero.gic.ericsson.se same Key used)
- https://arm.seli.gic.ericsson.se/artifactory/
- https://arm.epk.ericsson.se/artifactory/ (Redirects to arm.seli.gic.ericsson.se same Key used)

Example repositories.yaml File
```
repositories:
  - url: https://arm.rnd.ki.sw.ericsson.se/artifactory/
    username: "YYYYYYY"
    password: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  - url: https://arm.epk.ericsson.se/artifactory/
    username: "YYYYYYY"
    password: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  - url: https://arm.sero.gic.ericsson.se/artifactory/
    username: "YYYYYYY"
    password: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  - url: https://arm.seli.gic.ericsson.se/artifactory/
    username: "YYYYYYY"
    password: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Secret File
- File: <Choose the created repositories.yaml from the file system>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins)**
- Description: <Description of the added file>

#### Kubernetes Environment Config file
This is the kube config file that is used to log onto the kubernetes environment under test, this file should be the admin file
that all users can access. Do not use your own kube config file register under your user id. Please speak to your
environment admin for the correct file. Each environment that is to be deployed using CI should have a config file
stored in the Jenkins that will be used to execute the Jenkins job that is interacting with the kubernetes environment.

Parameter in the Jenkins file which uses these credentials, "KUBECONFIG_FILE"

Example config File
```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <LARGE SECRET>
    server: https://<kubernetes_cluster_IP>:6443
  name: <kubernetes_cluster>
contexts:
- context:
    cluster: <kubernetes_cluster>
    user: <USER>
  name: <USER & Cluster Name>
current-context: aispinn@hart105
kind: Config
preferences: {}
users:
- name: aispinn
  user:
    token: <LARGE TOKEN KEY>

```

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Secret File
- File: <Choose the config from the file system>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins)**
- Description: <Description of the added file>


### ADP DDC User Credentials

This is the username and password of the ADP DDC SFTP Server Credentials set as a secret within the Jenkins Credentials.

Parameter in the Jenkins file which use these credentials, "SFTP_CREDENTIALS"

To store the details open Jenkins in the Global Credentials area and Add Credentials
Select:
- Kind: Username and Password
- Scope Global .....
- Username: <SFTP Username>
- Password: <SFTP Password>
- ID: <Short Descriptive ID> **(This is the ID used in the Jenkins parameter to fetch the secret from Jenkins)**
- Description: <Description of the added secret>

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
