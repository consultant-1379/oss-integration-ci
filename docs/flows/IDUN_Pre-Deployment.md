# IDUN Pre Deployment Spinnaker Flow.

[TOC]

## Introduction

This spinnaker flow can be used to execute the IDUN pre deployment steps.
These steps are
- Common Deployment Steps
    * Namespace(s) Creation
    * Secret creation for eric-sec-access-mgmt-creds
    * Secret creation for eric-eo-database-pg-secret
    * Secret creation for eric-sec-access-mgmt-aapxy-creds
    * Secret creation for eric-odca-diagnostic-data-collector-sftp-credentials
    * Secret creation for testware-resources
    * Custom Cluster Role
- AM-Specific Pre-Deployment
    * Create a Cluster Role Binding
    * Secret creation for eric-appmgr-data-document-db-credentials

The Spinnaker flow covers the pre steps from the IDUN Deployment document.

Any updates needed to the site values, should be performed prior to executing the installation.

Please see the pre deployment steps in the installation document section for further details.

> **Note** This spinnaker flow should be used for IDUN only.

### Resources

The following is a link to the spinnaker flow
- [IDUN Pre Deployment Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=IDUN-Pre-Deployment)


## Stage And Parameter Overview

This is an overview of the pre steps, the parameters used and reference to the sections in
the deployment doc for each section:

- Namespace(s) Creation
    * This is the creation of the main name space and the crd namespace.
    * See the "Pre-Deployment" section of the IDUN Deployment instruction for more details.
    * The following parameters are involved with its creation
      ```
      Namespace                       (Namespace to perform the EO Deployment into)
      CRD Namespace                   (Namespace where the CRDs are deployed into)
      ```

- Secret creation for eric-sec-access-mgmt-creds
    * This is used for the creation of the generic secret called eric-sec-access-mgmt-creds for the IAM admin user
    * See the "Pre-Deployment" section of the IDUN Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Deployment Doc Reference

      Key Cloak Admin User                (KC_ADMIN_ID)
      Key Cloak Admin Password            (KC_PASSWORD)
      Key Cloak Postgres Admin User       (PG_USER_ID)
      KeyCloak Postgres Admin Password    (PG_PASSWORD)
      ```

- Secret creation for eric-eo-database-pg-secret
    * This is used for the creation of the secret called eric-eo-database-pg-secret for the Postgres admin user
    * See the "Pre-Deployment" section of the IDUN Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Deployment Doc Reference

      Postgres Custom User                (CUSTOM_USER_ID)
      Postgres Custom Password            (CUSTOM_PASSWORD)
      Postgres Super User ID              (SUPER_USER_ID)
      Postgres Super User Password        (SUPER_PASSWORD)
      Postgres Metrics User               (METRICS_USER_ID)
      Postgres Metrics Password           (METRICS_PASSWORD)
      Postgres Replica User ID            (REPLICA_USER_ID)
      Postgres Replica Password           (REPLICA_PASSWORD)
      ```

- Custom Cluster Role
    * This is used for the creation of the custom cluster role

       **Note:** Extra config to the site values required to use this section

   * See the "Pre-Deployment for EIAP Cluster Roles" section of the IDUN Deployment instruction for more details
   * The following parameters are involved with its creation
     ```
     Spinnaker Parameter                         Deployment Doc Reference

     Namespace                                   NAMESPACE_NAME
     CLUSTER_ROLE_BINDING_RELEASE_NAME           RELEASE_NAME
     ```

    * The Parameters above are used to set-up the PrivilegedPolicyClusterRole.yaml with the Proper naming convention.
    File structure (from CPI section Pre-Deployment Steps for Using a Custom Cluster Role):
    ```
    kind: ClusterRole
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: <RELEASE_NAME>-<NAMESPACE_NAME>-allowed-use-privileged-policy
      annotations:
        meta.helm.sh/release-name: <RELEASE_NAME>-<NAMESPACE_NAME>
        meta.helm.sh/release-namespace: <NAMESPACE_NAME>
        helm.sh/resource-policy: keep
      labels:
        app.kubernetes.io/managed-by: Helm
    rules:
    # Rule to allow privileged policy use in Openshift
      - apiGroups:
          - security.openshift.io
        resources:
          - securitycontextconstraints
        resourceNames:
          - privileged
        verbs:
          - use
    # Rule to allow privileged use in Kubernetes that uses Pod Security Policies
      - apiGroups:
          - policy
        resources:
          - podsecuritypolicies
        resourceNames:
          - privileged
        verbs:
          - use
    ```

- Secret creation for eric-sec-access-mgmt-aapxy-creds
    * This is used for the creation of the generic secret called eric-sec-access-mgmt-aapxy-creds, required when IAM is configured and AuthorizationProxy is enabled
    * This step is SEF-specific for now, so will not be referenced in CPI documentation for the time being
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Description

      ADP_IAM_AA_CLIENT_PASSWORD          IAM Password to use when creating the secret
      CI_DOCKER_IMAGE                     CI Docker image to use. Mainly used in CI Testing flows
      ENV_FILES_BUCKET_NAME               Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST
      FUNCTIONAL_USER_SECRET              Jenkins secret ID for a Functional user that has access to the data within DIT. ONLY USED if environment data store in OST
      GERRIT_REFSPEC                      RefSpec used for retrieving Jenkins job. Default: refs/heads/master
      KUBECONFIG_FILE                     Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename including the extension stored in OST
      NAMESPACE                           Namespace to create the secret in
      SECRET_NAME                         Name of the secret to create
      SLAVE_LABEL                         Specify the slave label that you want the job to run on
      ```

- Secret creation for eric-odca-diagnostic-data-collector-sftp-credentials
    * This is used for the creation of the SFTP Server generic secret called eric-odca-diagnostic-data-collector-sftp-credentials
    * See the "Pre-Deployment" section of the IDUN Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Description

      CI_DOCKER_IMAGE                     CI Docker image to use. Mainly used in CI Testing flows
      ENV_FILES_BUCKET_NAME               Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST
      FUNCTIONAL_USER_SECRET              Jenkins secret ID for a Functional user that has access to the data within DIT. ONLY USED if environment data store in OST
      GERRIT_REFSPEC                      RefSpec used for retrieving Jenkins job. Default: refs/heads/master
      KUBECONFIG_FILE                     Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename including the extension stored in OST
      NAMESPACE                           Namespace to create the secret in
      SFTP_CREDENTIALS                    Jenkins credentials consisting of a username and password for use when creating the SFTP Server secret
      SFTP_SECRET_NAME                    Name of the secret to create
      SLAVE_LABEL                         Specify the slave label that you want the job to run on
      ```

- Secret creation for testware-resources
    * This is used for the creation of secret, testware-resources-secret, which will be used in the testware infrastructure
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Description

      CI_DOCKER_IMAGE                     CI Docker image to use. Mainly used in CI Testing flows
      SECRET_NAME                         Name of the secret to create
      TESTWARE_API_URL                    The API URL for the Testware resource
      TESTWARE_DATABASE_URL               The Database URL for the Testware resource
      TESTWARE_K6_TOOL_GUI_URL            The GUI URL for the Testware resource
      ENV_FILES_BUCKET_NAME               Name of the Environment file OST bucket that stores the kube config file for the environment. ONLY USED if environment data store in OST
      FUNCTIONAL_USER_SECRET              Jenkins secret ID for a Functional user that has access to the data within DIT. ONLY USED if environment data store in OST
      GERRIT_REFSPEC                      RefSpec used for retrieving Jenkins job. Default: refs/heads/master
      KUBECONFIG_FILE                     Kubernetes configuration file to specify which test environment to connect to, this is either the Jenkins credentials ID or the filename including the extension stored in OST
      NAMESPACE                           Namespace to create the secret in
      SLAVE_LABEL                         Specify the slave label that you want the job to run on
      ```

- Create a Cluster Role Binding. (AM-Specific)
    * This is used for the creation of a service account for Container VNFM
    * See the "AM-Specific Pre-Deployment --> AM-Specific Role Binding" section of the IDUN Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      Namespace                                   NAMESPACE_NAME
      ```

- Secret creation for eric-appmgr-data-document-db-credentials (AM-Specific)
    * This is used for the creation of the secret called eric-appmgr-data-document-db-credentials for the app-mgr.
    * See the "AM-Specific Pre-Deployment --> AM Specific Secret for Helmfile Executor Database" section of the IDUN Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                 Deployment Doc Reference

      Postgres Custom User                (CUSTOM_USER_ID)
      Postgres Custom Password            (CUSTOM_PASSWORD)
      Postgres Super User ID              (SUPER_USER_ID)
      Postgres Super User Password        (SUPER_PASSWORD)
      Postgres Metrics User               (METRICS_USER_ID)
      Postgres Metrics Password           (METRICS_PASSWORD)
      Postgres Replica User ID            (REPLICA_USER_ID)
      Postgres Replica Password           (REPLICA_PASSWORD)
      ```
### Pipeline Maintenance
This flow is stored in a central repository for source-controlled Spinnaker pipelines.
The flow is stored in the following repo, [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory, cicd_pipelines_parameters_and_templates/dg_base/oss_product_flows.
Any changes made to the flow should be updated within this repo and sent to the Ticketmaster for review.
See the following document for more details on the use and rollout of updated flows, [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

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
