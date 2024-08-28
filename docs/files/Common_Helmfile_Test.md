# OSS Integration Common Helmfile Test JenkinsFile

[TOC]

## Introduction

This file is used to execute the Helmfile testing phase to execute tests like the static Helm validator tests etc.
against a given helmfile.

**NOTE**
- "HELMFILE NAME" referenced in this document is referring to the name of the helmfile when it is built, e.g.
  eric-eiae-helmfile-2.2392.0.tgz, application name would be **eric-eiae-helmfile**

## Prerequisites
In order to use this file there are a number of items that need to be in place, within the helmfile repo and the
oss-integration-ci repo.


### Helmfile Repo Requirements

- **ci/jenkins/site-values/k8s-compatibility-site-values.yaml**
  This is the site values file that is used during Kubernetes Compatibility Tests.
  For an example the following file can be seen: [Kubernetes Compatibility Site Values File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/master/ci/jenkins/site-values/k8s-compatibility-site-values.yaml)


- **testsuite/helm-chart-validator/site_values.yaml
  The "Generate Site Values File" will use a combination of the CI latest site values file for the product as the base yaml file and the testsuite site_values as an override file to generate a combined site values file.
  The combined site values file will be used during the Generate Optionality Maximum & Helmfile Validator Stage.
  Example base yaml file: [EIAE Site Values Latest File](../../site-values/idun/ci/template/site-values-latest.yaml)
  Example override file: [Testsuite Site Values File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/master/testsuite/helm-chart-validator/site_values.yaml)


### OSS Integration CI Repo Requirements

The following directory structure should exist:

- **testsuite/kubernetes-tests/kubeVersion.yaml**
  This determines which Kubernetes Versions will be tested against during Kubernetes Compatibility Tests stage.
  For an example the following file can be seen: [KubeVersion yaml file](../../testsuite/kubernetes-tests/kubeVersion.yaml)

- **testsuite/common/helmfile-validator/\*HELMFILE_NAME\*/skip_list.json** - This is the skip list for the helmfile
validator test. It lists the tests that can be skipped for the helmfile under test.
For an example see the following skips added for
[EIAE Helmfile Validator Skips](../../testsuite/common/helmfile-validator/eiae-helmfile/skip_list.json).
See Note Below.


- **testsuite/common/helmfile-validator/common_skip_list.json** - This is the common skip list which all Helmfiles
would be allowed to skip. An example is if a test is under development/all helmfiles are exempt from the test.
See the following for an example of the [Helmfile Validator Common Skip list](../../testsuite/common/helmfile-validator/common_skip_list.json).
See Note Below.


- **testsuite/helm-chart-validator/helm_file_plugin/file/plugin.yaml** -
  An example of files needed can be seen on: [Plugin.yaml](../../testsuite/helm-chart-validator/helm_file_plugin/file/plugin.yaml)


- **testsuite/helm-chart-validator/helm_file_plugin/file/bin/file.sh** -
  An example of files needed can be seen on: [File.sh](../../testsuite/helm-chart-validator/helm_file_plugin/file/bin/file.sh)


- Both above files will be used by the ci scripts image to ensure that File protocols can be handled.
  The File Protocol will be used during the "Generate Optionality Maximum" stage and will use to cache the charts used during Helmfile Template commands.

## Overview

Currently, when the file is executed it will:


- Set the build name


- Add a message to the Gerrit Review to indicate that a build has started for that review, if appropriate


- Clean down the Jenkins workspace before starting a new test flow


- Install the required Docker config which will be required to execute the different test phases.


- Build a new helmfile according to the GERRIT_REFSPEC or Helmfile Details inputted
  - If the Helmfile Details are inputted, the Helmfile will be fetched and tested on.
  - If a Gerrit Refspec is inputted, a new version of the Helmfile will be created based off the combination
    of the latest version of the Helmfile and the Gerrit Refspec, the new version will then be tested on.
  - If both Helmfile Details and Gerrit Refspec is inputted, GERRIT_REFSPEC takes priority.


- **Check files executable permission**, validates that any shell scripts or python files that are found within the
    Helmfile are executable.


- **Check shell scripts**, validates any shell scripts that are within the cloned repository (Including changed files within the GERRIT_REFSPEC).
  The ShellCheck tool identifies syntax issues within shell scripts. A detailed description of the ShellCheck tool can be found here: https://github.com/koalaman/shellcheck.


- **Lint YAML files**, uses the yamllint plugin in order to lint yaml files found within the cloned repository.
  This will ensure all files are adhering to the rules specified within the file: [Yamllint config file](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/9e0bca68a5b60b27e2b71f20b90084fc64942332/ci/jenkins/config/yamllint_config.yaml).


- **Validate Helm Chart Schema**, tests that the helm chart's JSON schema is valid.
  This JSON schema file should be called "values.json.schema" and located in the local chart's directory of the helmfile, e.g. [eric-eo-config JSON schema](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eo/eo-helmfile/+/master/helmfile/charts/eric-eo-config/values.schema.json).
  This stage can test one or multiple charts' schema.


- **Validate Helm Site-Values Schema**, tests the helmfile site-values-template against a JSON schema.
  The site-values-template file should be called "site-values-template.yaml" and located in the "templates" directory of the helmfile, e.g. [eric-eiae-helmfile site-values-template](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/refs/heads/master/helmfile/templates/site-values-template.yaml).
  The JSON schema file should be called "site-values-template.schema.json" and located in the base directory of the helmfile, e.g. [eric-eiae-helmfile JSON schema](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.eiae/eiae-helmfile/+/refs/heads/master/helmfile/site-values-template.schema.json).


- **Create Image Information Json File & Check if images exist on docker**, runs the following tests
  - These tests are to ensure the eric-product-info.yaml file within local charts for the Helmfile contain correct image information.
  - Correct image information will need to be verified in order to ensure that images can be pulled by the CSAR Builder when the --eric-product-info parameter is enabled.
  - The "Check if images exist on docker" stage will ensure that the docker images also exist on the registry through the use of the docker manifest inspect command.


- **Generate State Site Values File**, uses the latest site values file for the Helmfile stored within the oss-integration-ci repository
  - and the Helmfile Override Template File stored within the oss-integration-ci repository in order to generate an overall
  - site values file that will be used within various later stages.


- **Generate Optionality File**, generates an optionality_maximum file which will be used to ensure all services are enabled to be tested in the helmfile
  - and will cache resources used within the Helmfile Optimized folder to be used in later stages.


- **Run App validator Static Tests**, runs the following tests:

  >> **Note:** If your application is exempted from one of these tests please see the following section, [Skip Test](#skip-tests)
       on how to add your application to the skip lists. ( Note: All code snippets referenced below can be seen
       [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/etc/testsuite/helmfile-validator/))

  - Test Default Storage Class Name
    - This module contains test cases to verify that only the default storage class is referenced.
      ```
       if kind != 'CustomResourceDefinition':
         assert storage_class_name is None
      ```

  - Test To Ensure all Containers With "Securitycontext" has "runAsNonRoot" set
    - Ensures that there is a runAsNonRoot set with appropriate permission associated with each security context
      set for pods and containers.
      ```
       assert type(resulting_security_context.get('runAsNonRoot', None)) is bool
      ```

  - Test to Ensure all CVNFM Contains do not have "runAsUser" set within "SecurityContext"
    - Ensures that there is no runUser parameter set associated to each security context
     ```
      assert resulting_security_context.get('runAsUser', None) is None
     ```


  - Test Validate Minimum Replica Count
    - Ensures that specified services reached the minimum replica count required for EIC.


  - Test Validate Minimum Replica Count EO
    - Ensures that specified services reached the minimum replica count required for EO.

- **Lint - Helmfile Build Output**, This stage is used to ensure the "helmfile build" yaml template is valid yaml.


- **Run Kubernetes Range Compatibility Tests**, this stage runs a number of compatibility tests on the Kubernetes objects in the charts inside the Helmfile.
    - *Note:* Please read the [Kubernetes Range Compatibility Tests Documentation](../Kubernetes_Range_Compatibility_Tests.md) for further information on the scripts that run and the rulesets used in this section.


### Skip Tests
A helmfile can add a skip for a specified test to a skip file for any of the tests within the Helmfile Validator Stage either as a specific skip for a certain application or on a common list that will be skipped for all
helmfiles executing this stage.

The skip lists are currently part of the oss-integration-ci code base within the following area of the
repo, [helmfile-validator skip list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helmfile-validator/)

#### Helmfile Validator Skip Test

Inside the [helmfile-validator skip list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helmfile-validator/)
there is a [common_skip_list.json](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helmfile-validator/common_skip_list.json).
This lists all the common skips. Whatever entries are in this list will be skipped for all applications. For skips for a
specific helmfile there will be a directory, named with the helmfile name (HELMFILE NAME), that lists all the skips for that helmfile, e.g.
[eiae-helmfile](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helmfile-validator/eiae-helmfile/) skip list

The structure of the skip for each of the tests are in the following format
```
  "<NAME_OF_THE_TEST_TO_BE_SKIPPED>": {
      "skips": [
        [["<Service Name>"], ["<Template Kind To be Skipped>"], "<Description why it is exempt and JIRA Number>", "skip"]
      ],
      "runTests": true
  },
```
Note: All the test names (i.e. <NAME_OF_THE_TEST_TO_BE_SKIPPED>) can be seen
[here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/etc/testsuite/helmfile-validator/)
E.G.
```
  "test_post_install_is_used_in_post_upgrade_service_hook": {
      "skips": [
          [["eric-gr-bur-orchestrator-hook-role"], ["Role"], "Exempted via SM-122081, openshift test failing in app staging pre code tests.", "skip"],
      ],
      "runTests": true
  },
```

Note: If a complete test section for an application is exempt or not applicable for that application then the full tests can be
skipped by setting the runTests to false within the test section.
```
"test_post_install_is_used_in_post_upgrade_service_hook": {
      "skips": [],
      "runTests": false
  },
```
To add a skip to this list please contribute the review and the exemption approval from ODP and send to Ticketmaster for
final sign off, please see the [Contributing Guide](../Contribution_Guide.md) for details.


### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/helmfile/pcr/commonHelmfileTest.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following job is used within the Base and Product staging flows
- [Jenkins Jobs]()

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Default                                                                  |
|-------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| GERRIT_REFSPEC                            | Gerrit refspec of the helmfile under tests example: refs/changes/88/9999988/9 - 88 - last 2 digits of Gerrit commit number / 9999988 - is Gerrit commit number / 9 - patch number of gerrit commit                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                          |
| GERRIT_PROJECT                            | Gerrit project details e.g. OSS/com.ericsson.oss.eiae/eiae-helmfile                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                          |
| GERRIT_PATCHSET_REVISION                  | Revision string for the gerrit review. Example: Ieec3b0b65fcdf30872befa2e9ace06e96cd487b4.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                          |
| GERRIT_USER_SECRET                        | Jenkins secret ID with Gerrit username and password                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                          |
| FUNCTIONAL_USER_SECRET                    | Jenkins secret ID for ARM Registry Credentials.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                          |
| ARMDOCKER_USER_SECRET                     | Jenkins secret ID with ARM Docker config details.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                          |
| INT_CHART_NAME                            | Helmfile name which is used during the Fetch Helmfile Repo stage eg. eiae-helmfile. GERRIT_REFSPEC should be blank if using this value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                                                          |
| INT_CHART_VERSION                         | Helmfile version which is used during the Fetch Helmfile Repo Stage eg.2.2438.0. GERRIT_REFSPEC should be blank if using this value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                          |
| INT_CHART_REPO                            | Helmfile url which is used during the Fetch Helmfile Repo Stage. E.g.: https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/. GERRIT_REFSPEC should be blank if using this value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                                                          |
| CHART_PATH                                | Relative path to helmfile local charts in the git repo. Multiple charts must be passed as a csv String, e.g. charts/eric-eo-config,charts/eric-eo-config-test,charts/eric-eo-test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                          |
| PATH_TO_SITE_VALUES                       | The full path to the ci site values template file for the Helmfile under test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                          |
| PATH_TO_SITE_VALUES_OVERRIDE_FILE         | The full path to the ci site values override template file for the additional values needed for the Helmfile under test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                          |
| KUBERNETES_COMPATIBILITY_SITE_VALUES_PATH | The full path to the kubernetes compatibility site values file used during the Kubernetes Testing Phase                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                          |
| HELMFILE_NAME                             | The name of the Helmfile under test e.g. eiae-helmfile/eo-helmfile. Very important as it is used to set the build name and conditionally run certain Helmfile-specific stages                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                          |
| KUBEVAL_KINDS_TO_SKIP                     | Skipped Kubeval checks for specific kinds. Current skips for eo-helmfile - "HTTPProxy,CertificateAuthority,ClientCertificate,InternalCertificate,InternalUserCA,ServerCertificate,CustomResourceDefinition,DestinationRule,EnvoyFilter,PeerAuthentication,Gateway,Sidecar,Telemetry,template,VirtualService,CassandraCluster,Kafka,KafkaBridge,ExternalCertificate,RedisCluster". Current skips for eiae-helmfile - "HTTPProxy,ServerCertificate,InternalCertificate,ClientCertificate,CertificateAuthority,adapter,attributemanifest,AuthorizationPolicy,CustomResourceDefinition,CassandraCluster,DestinationRule,EnvoyFilter,Gateway,handler,HTTPAPISpec,HTTPAPISpecBinding,instance,PeerAuthentication,QuotaSpec,QuotaSpecBinding,RbacConfig,RequestAuthentication,rule,ServiceEntry,ServiceRole,ServiceRoleBinding,Sidecar,Telemetry,template,VirtualService,WorkloadEntry,WorkloadGroup,Kafka,KafkaBridge,RedisCluster,ExternalCertificate,InternalUserCA" |                                                                          |
| SPINNAKER_PIPELINE_ID                     | ID of the associated Spinnaker pipeline. Used as a placeholder in order to mitigate Jenkins 404 errors.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 123456                                                                   |
| TIMEOUT                                   | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT                    | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT                  | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 300                                                                      |
| SLAVE_LABEL                               | Specify the slave label that you want the job to run on.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | evo_docker_engine                                                        |
| VCS_BRANCH                                | Branch for the change to be pushed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | master                                                                   |
| CI_DOCKER_IMAGE                           | CI Docker image to use. Mainly used in CI Testing flows                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| CI_REFSPEC                                | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

Artifacts that will be outputted from the Jenkins Job:
  - The site_values.yaml generated by the "Generate Site Values" stage.
  - The report (helmfile-validator-test-report.html) generated by the "Run Helmfile Openshift Static Tests" stage.
  - The image_information_list.json which showcases the images gathered in local charts of the Helmfile during the "Validating eric-product-info images" stage.

## Execution options
The testing phase job for a helmfile may need to be executed in two different ways,
- where the testing phase is executed as part of a spinnaker flow, ie when a new application version is being included within the helmfile.
- during a gerrit push, to apply a verified +1 on the code review, i.e. PCR

### Execute through a spinnaker flow
To execute within a spinnaker flow the Common testing Jenkins file needs to be created on the Jenkins server, see [Jenkins Job Configuration](#Jenkins-Job-Configuration)

If the job is created,
- Link the job to the appropriate spinnaker flow
- See the [Parameters](#Parameters) Section for an explanation on what parameters are needed for the helmfile under test.

### Execute Post Gerrit Push
To execute the PCR post a gerrit push, so it applies a verified +1 to the review. This is achieved by applying a second
Jenkins file to execute the helmfile common testing Jenkins file.

A second Jenkins file is needed due to the fact that Jenkins uses gerrit triggers, to execute a job. This limits the
amount of details that can be sent to Helmfile Common testing Jenkins job directly, so there needs to be an extra Jenkins job
per helmfile configured, this job will be triggered by the Gerrit event and will have the helmfile info preconfigured
so the correct details are sent to the common testing job.

Two Jenkins jobs are required to be created,
- Helmfile Common Testing Jenkins job,
  - See the [Jenkins Job Configuration](#Jenkins-Job-Configuration) on how to create this job, if not already created.
  - Ensure the job created matches the value given within PCR_MASTER_JOB_NAME parameter from the trigger job jenkinsfile [Helmfile In Review PCR Testing Jenkins File](Helmfile_In_Review_Common_PCR_Testing.md), as this will be needed for the next step.
- Helmfile PCR Job,
  - This is the job that will get triggered by the Gerrit Event. See the following page for info on the
    [Helmfile In Review PCR Testing Jenkins File](Helmfile_In_Review_Common_PCR_Testing.md)

  >> ** Note: The following naming convention is recommended <Helmfile Name>-PCR-From-Review e.g. EO-Helmfile-PCR-From-Review
  - When the job is created configure the following within the **configuration** of the job.
  >> **Note:**
  > The below commands should be executed in the job configuration and permanently stored in the configuration of the job
  - **Parameters Section**
    - Add the appropriate values to the **Default Values** section in the job, that are associated to the helmfile under
      test. These will be the default values going forward and will not be overwritten when the Jenkins file executes.
  - **Gerrit Trigger**
    - Under "Gerrit Project",
      - Type : Set to Plain
      - Pattern : Add the Gerrit project address
      - Branch :
        - Type : Set to Path
        - Pattern : Set to **/\*

  - Save. On the next push to gerrit for review the job should execute and give a verified +1 if it passes or
    a verified -1 on a failure.

  >> **Note:**
  > In order for Feedback to be obtained, ensure that the user executing the job has the required permissions to apply a +1/-1 Verified within the Gerrit Access Configuration of the Helmfile Repository

## Jenkins Job Configuration

> **Note:** to create a new Jenkins job the user should have the correct access rights to the Jenkins server

If the job needs to be created on a Jenkins server, the following needs to be followed

- Create a new Pipeline Jenkins Job
- Within the "Pipeline Section" of the Jenkins Job Configuration set the following
    * **Definition:** Pipeline script from SCM
    * **SCM:** Git
    * **Repositories URL:** ${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    * **Credentials:** Choose appropriate credentials for Gerrit cloning
    * **Branches to build:** FETCH_HEAD
    * **Advanced - Refspec:** ${CI_REFSPEC}
    * **Advanced Behaviours - Advanced Clone Behaviours:** Honor refspec on initial clone
    * **Advanced Behaviours - Advanced Clone Behaviours:** Shallow Clone - Shallow Clone depth - 1
    * **Script Path:** ci/jenkins/files/helmfile/pcr/commonHelmfileTest.Jenkinsfile
> **Note:** Once the repo has been configured in the Jenkins job, there is no need to configure the parameters, the job on execution
will automatically create all the parameter(s) on the first execution. The job will fail though.


### Testing

In order to test a Jenkins file (Without affecting the master branch), please refer to the [Contributing Guide](../Contribution_Guide.md).

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
