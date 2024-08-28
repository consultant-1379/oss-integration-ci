# EO Pre Deployment Spinnaker Flow.

[TOC]

## Introduction

This spinnaker flow can be used to execute the EO pre deployment steps.
These steps are
- Common Deployment Steps
    * Namespace(s) Creation
    * Secret creation for eric-sec-access-mgmt-creds
    * Secret creation for eric-eo-database-pg-secret
    * Custom Cluster Role
- EVNFM Pre Deployment
    * Create a Service Account
    * Create a Cluster Role Binding
    * Create a generic secret --> Option 1: Deploy using Internal Container Registry
- ENM Secret Creation
    * ENM Secret Creation for Container EVNFM
    * ENM Secret Creation for VM VNFM

The Spinnaker flow covers the pre steps from the EO Deployment document.

Any updates needed to the site values, should be performed prior to executing the installation.

Please see the pre deployment steps in the installation document section for further details.

> **Note** This spinnaker flow should be used for EO only.

### Resources

The following is a link to the spinnaker flow
- [EO Pre Deployment Spinnaker Flow](https://spinnaker.rnd.gic.ericsson.se/#/projects/oss_e2e_cicd/applications/common-e2e-cicd/executions?pipeline=EO-Pre-Deployment)


## Stage And Parameter Overview

This is an overview of the pre steps, the parameters used and reference to the sections in
the deployment doc for each section:

- Namespace(s) Creation
    * This is the creation of the main name space and the crd namespace.
    * See the "Pre-Deployment" section of the EO Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Namespace                       (Namespace to perform the EO Deployment into)
      CRD Namespace                   (Namespace where the CRDs are deployed into)
      ```

- Secret creation for eric-sec-access-mgmt-creds
    * This is used for the creation of the generic secret called eric-sec-access-mgmt-creds for the IAM admin user
    * See the "Pre-Deployment" section of the EO Deployment instruction for more details
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
    * See the "Pre-Deployment" section of the EO Deployment instruction for more details
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
    * This is used for the creation of the custom cluster role.

       **Note:** Extra config to the site values required to use this section
   * See the "Pre-Deployment for EO Cluster Roles" section of the EO Deployment instruction for more details
   * The following parameters are involved with its creation
     ```
     Spinnaker Parameter                         Deployment Doc Reference

     Namespace                                   NAMESPACE_NAME
     Service Account & Cluster Role B Meta Name  RELEASE_NAME
     ```
    * The Parameters above are used to set-up the EOPrivilegedPolicyClusterRole.yaml with the Proper naming convention.
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

- Create a Service Account (EVNFM Specific)
    * This is used for the creation of a service account for Container VNFM
    * See the "EVNFM-Specific Pre-Deployment --> Create a Service Account" section of the EO Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      Namespace                                   NAMESPACE_NAME
      Service Account & Cluster Role B Meta Name  metadata.name: <SERACC_CLSROLB_META_NAME>
      ```
    * The Parameters above are used to set-up the ServiceAccount.yaml with the Proper naming convention.
    File structure (from CPI section EVNFM-Specific Pre-Deployment):
    ```
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: <SERACC_CLSROLB_META_NAME>
    automountServiceAccountToken: true
    ```

- Create a Cluster Role Binding. (EVNFM Specific)
    * This is used for the creation of a service account for Container VNFM
    * See the "EVNFM-Specific Pre-Deployment --> Create a Cluster Role Binding" section of the EO Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      Namespace                                   NAMESPACE_NAME
      Service Account & Cluster Role B Meta Name  metadata.name: <SERACC_CLSROLB_META_NAME>
      ```
    * The Parameters above are used to set-up the ServiceAccount.yaml with the Proper naming convention.
    File structure (from CPI section EVNFM-Specific Pre-Deployment):
    ```
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: <SERACC_CLSROLB_META_NAME>
    automountServiceAccountToken: true
    ```

- Create a generic secret --> Option 1: Deploy using Internal Container Registry (EVNFM Specific)
    * This is used for the creation of a generic secret for the EVNFM container registry service.
    * See the "EVNFM-Specific Pre-Deployment --> Option 1: Deploy using Internal Container Registry" section of the EO Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      Internal Container Registry User ID         USER_ID
      Internal Container Registry User Password   USER_PASSWORD
      ```
    * The Parameters above are used to create a htpasswd that are used to generate the Internal Registry secret.

    **Note:**
    * <USER_ID> must match the <eric-eo-evnfm-nbi.eric-evnfm-rbac.defaultUser.username> in the site values file.
    * <USER_PASSWORD> must match the <eric-eo-evnfm-nbi.eric-evnfm-rbac.defaultUser.password> in the site values file.

- ENM Secret Creation for Container EVNFM
    * This is used for the creation of a secret to be able to connect ENM and Container VNFM

        **Note:** Extra config to the site values required to use this section

    * See the "Configure ENM and EVNFM Connectivity" section of the EO Deployment instruction for more details
    * This section can be skipped by setting the parameter, "CONFIGURE_ENM_AND_VNFM_CONNECTIVITY" to false.
      ```
      Spinnaker Parameter

      CONFIGURE_ENM_AND_VNFM_CONNECTIVITY =  false
      ```
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      ENM Container Secret Name                   ENM_SECRET_NAME
      ENM Container Scripting Cluster IP          ENM_SCRIPTING_CLUSTER_IP
      ENM Container Secret Username               ENM_USERNAME
      ENM Container Secret password               ENM_PASSWORD
      ENM Connection timeout (milli seconds)      ENM_CONNECTION_TIMEOUT_IN_MILLISECONDS
      ENM Container Scripting SSH Port            ENM_SCRIPTING_SSH_PORT
      ```

- ENM Secret Creation for VM VNFM
    * This is used for the creation of a secret to be able to connect ENM and VM VNFM

        **Note:** Extra config to the site values required to use this section
    * This section can be skipped by setting the parameter, "CONFIGURE_ENM_AND_VNFM_CONNECTIVITY" to false.
      ```
      Spinnaker Parameter

      CONFIGURE_ENM_AND_VNFM_CONNECTIVITY =  false
      ```
    * See the "Configure ENM and EVNFM Connectivity --> VM VNFM with ENM Connectivity" section of the EO Deployment instruction for more details
    * The following parameters are involved with its creation
      ```
      Spinnaker Parameter                         Deployment Doc Reference

      ENM Master Service IP                       ENM_MASTER_SERVICE_IP
      ENM Notification Service IP                 ENM_NOTIFICATION_SERVICE_IP
      ENM_MASTER_SERVER_HOSTNAME                  Enm Master Server Hostname
      ENM_NOTIFICATION_SERVICE_HOSTNAME           ENM Notification Service Hostname

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
