## Kubectl Executor

[TOC]

## Introduction
This is the main executor for executor Kubernetes commands.

The commands available for use through this executor are listed below.

## Execute "kubectl_executor" help
```
docker run armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:<VERSION> kubectl_executor --help
```

## Available commands
| Command                                   | Description                                                                                                                                                                                             | Link                                                                                         |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| check-and-create-internal-registry-secret | Creates a registry secret on a namespace, will not create if the registry secret already exists.                                                                                                        | [Check_And_Create_Internal_Registry_Secret.md](Check_And_Create_Internal_Registry_Secret.md) |
| create-cluster-rolebinding                | Creates a cluster role binding on a namespace, will not create if the role binding already exists.                                                                                                      | [Create_Cluster_Rolebinding.md](Create_Cluster_Rolebinding.md)                               |
| create-common-resources                   | Create common resources on a namespace for deployment (ConfigMap object for the testware hostnames, configMap object for the global testware configuration and secret object for the DDP configuration) | [Create_Common_Resources.md](Create_Common_Resources.md)                                     |
| create-generic-secret-from-literals       | Creates a generic secret on a namespace using a CSV of space-seperated literals, will not create if the generic secret already exists.                                                                  | [Create_Generic_Secret_From_Literals.md](Create_Generic_Secret_From_Literals.md)             |
| create_namespace                          | Creates a namespace on the cluster, if the namespace already exists the command will fail unless ignore_exists is set to true.                                                                          | [Create_Namespace.md](Create_Namespace.md)                                                   |
| create-namespace-secret                   | Creates the namespace secret on a namespace, namespace secret will be deleted unless ignore_exists is set to true.                                                                                      | [Create_Namespace_Secret.md](Create_Namespace_Secret.md)                                     |
| create-privileged-policy-cluster-role     | Creates a privileged policy cluster role on a namespace, will not create if the privileged policy cluster role already exists.                                                                          | [Create_Privileged_Policy_Cluster_Role.md](Create_Privileged_Policy_Cluster_Role.md)         |
| create-resource-with-yaml-file            | Creates a Kubernetes resource with a provided YAML file on a namespace, will not create  if the resource exists.                                                                                        | [Create_Resource_With_Yaml_File.md](Create_Resource_With_Yaml_File.md)                       |
| create-service-account                    | Creates a service account on a namespace, will not create if the service account already exists.                                                                                                        | [Create_Service_Account.md](Create_Service_Account.md)                                       |
| create-server-event-variables             | Creates and gathers the server event variables to a properties file.                                                                                                                                    | [Create_Server_Event_Variables.md](Create_Server_Event_Variables.md)                         |
| delete-namespace                          | Deletes a specified namespace, will fail if the namespace does not exist.                                                                                                                               | [Delete_Namespace.md](Delete_Namespace.md)                                                   |
| remove-cluster-roles                      | Deletes a cluster role from a namespace, will fail if the cluster role does not exist.                                                                                                                  | [Remove_Cluster_Roles.md](Remove_Cluster_Roles.md)                                           |
| remove-cluster-role-bindings              | Deletes a cluster role binding from a namespace, will fail if the cluster role binding does not exist.                                                                                                  | [Remove_Cluster_Role_Bindings.md](Remove_Cluster_Role_Bindings.md)                           |
| remove-kafka-topic-resources              | Removes kafka topic resources from a namespace.                                                                                                                                                         | [Remove_Kafka_Topic_Resources.md](Remove_Kafka_Topic_Resources.md)                           |
| uds-backend-job-wait                      | Waits for uds job to complete, will fail after specified time in namespace.                                                                                                                             | [Uds_Backend_Job_Wait.md](Uds_Backend_Job_Wait.md)                                           |
| wait-for-persistent-volumes-deletion      | Wait for persistent volumes to be deleted from a namespace.                                                                                                                                             | [Wait_For_Persistent_Volumes_Deletion.md](Wait_For_Persistent_Volumes_Deletion.md)           |
| get-value-from-configmap-or-secret        | Search for string within kubectl resource, secret or configmap.                                                                                                                                         | [Get_Secret_or_Configmap_Date.md](Get_Secret_or_Configmap_Date.md)                           |

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
