## Deployment Related Jenkins Files
As a CI developer, I want to configure a Jenkins Job to create a namespace in a cluster.

[OSS Create a new namespace within the given cluster](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Create_Namespace.md)

As a CI developer, I want to completely clean down the namespace and all its associated resources.

[Removes the namespace and all associated resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Purge.md)

As a CI developer, I want to create a new namespace secret within the given cluster using the docker secret as the credentials.

[OSS Create a new namespace secret within the given cluster using the docker secret as the credentials](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Create_Namespace_Secret.md)

As a CI developer, I want to create the secret that is required for the Container VNFM and the ENM connectivity.

[Secret Creation for Container VNFM to ENM Connectivity](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/ENM_Container_VNFM_Connectivity.md)

As a CI developer, I want to create the secret that is required for the VM VNFM and the ENM connectivity.

[Secret Creation for VM VNFM to ENM Connectivity](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/ENM_VM_VNFM_Connectivity.md)

As a CI developer, I want to ensure that the deployment is in a good state, so I can execute any tests on the system

[OSS Check Helmfile Deployment Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Check_Helmfile_Deployment.md)

As a CI developer, I want to gather all the environment details for a given environment.

[OSS Gather Environment Details Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Gather_Environment_Details.md)

As a CI developer, I want to gather the logs for a specific environment.

[OSS Get Kubernetes Logs Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Get_Kubernetes_Logs.md)

As a CI developer, I want to execute the deployment using a given helmfile.

[OSS Helm File Deploy Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Helmfile_Deploy.md)

As a CI developer, I want to execute the deployment using a given helmfile and fetch the environment details using the Deployment Inventory Tool (DIT).

[OSS Helmfile Deploy Jenkins File using the Deployment Inventory Tool (DIT)](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Helmfile_Deploy_Using_DIT.md)

As a CI developer, I want to quarantine a resource from the lockable resources within jenkins.

[Quarantine Environment Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Quarantine_Resource.md)

As a CI developer, I want to reserve a resource from the lockable resources within jenkins.

[Reserve Environment Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Reserve_Resource.md)

As a CI developer, I want to unreserve a resource from the lockable resources within jenkins.

[Unreserve Environment Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Unreserve_Resource.md)

As a CI developer, I want to execute the EVNFM Specific pre-deployment steps.

[EVNFM Pre Deployment Steps](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/EVNFM_Pre-Deployment.md)

As a CI developer, I want to execute the AM Specific cluster role binding creation.

[AM Specific Cluster Role Binding Creation](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/AM-Specific_Role_Binding.md)

As a CI developer, I want to create a custom cluster role, so I can perform pre-deployment steps.

[Custom Cluster Role Creation](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Custom_Cluster_Role.md)

As a CI developer, I want to create the Postgres Database secret.

[Postgres Database Secret Creation](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Database-PG_secret.md)

As a CI developer, I want to create the generic secret called eric-sec-access-mgmt-creds for the IAM admin user.

[Generic secret for the IAM admin](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Eric-Sec-Access-Mgmt-Creds_Secret.md)

 As a CI developer, I want to create the generic secret called eric-sec-access-mgmt-aaxpy-creds specific for SEF when IAM is installed with Authentication Proxy.

[Generic SEF specific secret](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Eric-Sec-Access-Mgmt-Aapxy-Creds_Secret.md)

As a CI developer, I want to execute a health check of a deployment using Deployment Manager Health Check functionality, so I can get snapshot view of health of workloads/network/storage in the deployed kubernetes cluster.

[OSS Health Check using Deployment Manager](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Health_Check_Using_Deployment_Manager.md)

----

## Miscellaneous Jenkins files stored and referenced from the oss-integration ci repo

As a CI developer, I want to get all the Application names and version included in a given helmfile.

[OSS Calculate App Versions From Helmfile Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Calculate_App_Versions_From_Helmfile.md)

As a App Eng team, I want to check if the content being added to the eric-product-info.yaml file of an application is able to be pulled down by the CSAR Builder with given image information.

[Check Eric Product Info Information Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Check_Eric_Product_Info_Information.md)

As a CI developer, I want to return the status of a job to Gerrit History.

[OSS Gerrit Notification Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Gerrit_Notification.md)

As a CI developer, I want to be able to get the latest helmfile version from a given arm repository.

[Get Latest Chart or Helmfile Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Get_Latest_Chart_Or_Helmfile.md)

As a CI developer, I want to check whether an application should be an official release or not, after testing has been completed.

[ADP PRA Version check Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Check_App_For_Official_Delivery.md)

As a CI developer, I want to gather the release info from a given Helmfile.

[Get Release Info From Helmfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Get_Release_Info_From_Helmfile.md)

As a CI developer, I want to gather the microservice details present inside the product helmfiles.

[OSS Gather Microservices information from Helmfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Get_Microservice_Info_From_Helmfile.md)

As a CI developer, I want to get CRD tar file information from a given application chart.

[Get the CRDs from a given chart](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Check_For_CRDs.md)

 As a CI developer, I want to assess whether all the services contained within the CNCS Chart.yaml file are also contained within the optionality.yaml file of the helmfile.

[OSS CNCS Optionality Checker](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/CNCS_Optionality_Checker.md)

As a CI developer, I want to update the Deployment manager (DM) version in the specified Product Helmfile.

[OSS Update DM Version in Product Helmfile and push review](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Update_DM_Version_In_Product_Helmfile.md)

As a CI developer, I want to be able to compare the current versions of applications in a Helmfile to the latest versions in the relevant repos.

[OSS Compare Application Versions From Helmfile Jenkins File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/Compare_Latest_Versions_In_Helmfile.md)


