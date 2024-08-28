# OSS Integration Common Test JenkinsFile

[TOC]

## Introduction

This file is used to execute the Application testing phase to execute tests like the static Helm validator test and the
ADP design rules tests against a given helm chart.

**NOTE**
- "APP NAME" referenced in this document is referring to the name of the chart when it is built, e.g.
eric-oss-common-base-0.4.2-19.tgz, application name would be **eric-oss-common-base**
- "APP_CHART" referenced in this document referring to the full name and version given to the chart when it is built,
e.g.eric-oss-common-base-0.4.2-19.tgz

## Prerequisites
In order to use this file there are a number of items that need to be in place, within the chart repo and the
oss-integration-ci repo.

### Chart Repo Requirements

The following directory and files structure should exist

- testsuite/site_values.yaml
- testsuite/schematests/tests/negative
- testsuite/schematests/tests/positive

The following files should exist

- **testsuite/site_values.yaml** - This is a site values file that is used to perform a helm template against the chart
under test. It will be used during the helm-chart-validator tests and the ADP design rule tests. This site values should
have all the parameters required to template out the full chart template. For an example of this structure see
[OSS-Common-Base Site Values](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss/oss-common-base/+/refs/heads/master/testsuite/site_values.yaml)


**Note** One of the test ensures the pull secet and the registry is being added to the templates, so the site values
should have the following set,
```
global:
  registry:
    url: "dummy.rnd.ericsson.se"
    username: "dummyusername"
    password: "dummypassword"
  pullSecret: "dummy-pull-secret"
```


- **testsuite/schematests/tests/negative** and **testsuite/schematests/tests/positive** - These directories hold the schema
tests that should be executed to verify the schema yaml file that is created for the application chart.
This schema should be found within the application chart directory (i.e. charts/<APP_NAME>
e.g. charts/eric-oss-common-base see
[OSS-Common-base Schema File](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss/oss-common-base/+/refs/heads/master/charts/eric-oss-common-base/values.schema.json)
as an example).
See the following for an example of the
[OSS-Common-Base Negative and Positive schema tests](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss/oss-common-base/+/refs/heads/master/testsuite/schematests/tests/)


### OSS Integration CI Repo Requirements

The following directory structure should exist

- **testsuite/common/adp_design_rule/\*APP_NAME\*/design_rule_options.txt** - This holds the ADP design rule options
including the skips for the specific application under test.
For an example see the following design rule options for
[OSS-Common-Base ADP Design Rule Options](../../testsuite/common/adp_design_rule/eric-oss-common-base/design_rule_options.txt).
See Note Below


- **testsuite/common/adp_design_rule/common_design_rule_options.txt** - This is common design rule options file, this is used to set
certain design rules that may need to be set from all applications executing these tests, this maybe used when new design
rules are being introduced etc or when certain ADP design rule config needs to be set across all the applications.
See the following for an example of the [ADP Design Rule Common Options list](../../testsuite/common/adp_design_rule/common_design_rule_options.txt).
See Note Below.


- **testsuite/common/helm-chart-validator/\*APP_NAME\*/skip_list.json** - This is the skip list for the helm chart
validator test, it lists the tests that can be skipped for the application under test.
For an example see the following skips added for
[OSS-Common-Base Helm Chart Validator Skips](../../testsuite/common/helm-chart-validator/eric-oss-common-base/skip_list.json).
See Note Below.

- **testsuite/common/helm-chart-validator/common_skip_list.json** - This is the common skip list which all applications
would be allowed to skip, example of this maybe ADP component, the ADP component are exempt from these tests.
See the following for an example of the [Helm Chart Validator Common Skip list](../../testsuite/common/helm-chart-validator/common_skip_list.json).
See Note Below.


**NOTE:**
  - The Common Skip lists should only be updated by the ODP Team over design Rule exemptions.
  - Any skip/exemptions/rule being added to any of the above files need to be pre-approved from the ODP team, please see the
following page for more details [Obtain a Design Rule Exemption](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=ODP&title=Obtain+a+Design+Rule+Exemption).

## Overview

Currently, when the file is executed it will:

- Clean down the Jenkins workspace before starting a new test flow


- Install the required Docker config which will be required to execute the different test phases.


- Build a new chart according to the GERRIT_REFSPEC or Chart Details inputted
  - Two options can be used here, ADP's INCA or ADP CI Helm, this is set according to the Parameters set within the job,
  see [Parmaters](#Parameters) section for details


- **Run App validator Schema Tests**, runs the following tests.
    - Tests that the Helm chart JSON schema is valid.
      - The JSON schema should be contained within the base directory of the packaged chart.
      - The JSON schema file should be called "values.json.schema".
    - Runs the negative schema tests contained within the chart repository. These tests run a Helm template against different invalid YAML files to ensure the helm template fails, and fails for the correct reason.
      - This directory should contain site values files which will result in an error when used to run a Helm template against the chart.
      - Each site values file should have a corresponding text file containing the expected Helm stderr output.
      - The names of the site values files and text files should be identical, except with "_expected_errors" appended to the end of the text file.
      - For example, a YAML file with an invalid "username" parameter would be called "test_invalid_username.yaml", and the text file containing the expected output would be called "test_invalid_username_expected_errors.txt".
      - An example can be found here: [OSS Common Base Negative Schema Tests](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss/oss-common-base/+/refs/heads/master/testsuite/schematests/tests/negative/)
    - Runs the positive schema tests contained within the chart repository. These tests run a helm template against different valid site values files to ensure the helm template passes.
      - This directory should contain site values files which will yield a successful Helm template command against the chart.
      - An example can be found here: [OSS Common Base Positive Schema Tests](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss/oss-common-base/+/refs/heads/master/testsuite/schematests/tests/positive/)


- **Check shell scripts**, validates any shell scripts that are within the cloned repository (Including changed files within the GERRIT_REFSPEC).
  The ShellCheck tool identifies syntax issues within shell scripts. A detailed description of the ShellCheck tool can be found here: https://github.com/koalaman/shellcheck.


- **Python lint** runs a series of static checks against any Python modules contained within the chart.
    These checks include pylint, flake8, and pydocstyle to ensure any Python code is presented and documented correctly.
    This stage only runs when Python modules have been changed as part of the commit. Otherwise, this stage is skipped.


- **Helm lint**, runs the following tests
  - This command takes a path to a chart and runs a series of tests to verify that the chart is well-formed.
  - It executes a command like so
  ```
    helm lint <WORKSPACE>/<APP NAME> --values <WORKSPACE>/<BOD TEMP REPO>/testsuite/helm-chart-validator/site_values.yaml
  ```
  **Note:**
  - \<WORKSPACE>/\<APP NAME> represents the chart that was built using the review under test and extracted.
  - The values file passed to it, is the site values from the testsuite/helm-chart-validator/ directory from the repo under test.


- **Create Image Information Json File & Check if images exist on docker**, runs the following tests
  - These tests are to ensure the eric-product-info.yaml file within the chart & subcharts contain correct image information
  - Correct image information will need to be verified in order to ensure that images can be pulled by the CSAR Builder when the --eric-product-info parameter is enabled
  - The "Check if images exist on docker" stage will ensure that the docker images also exist on the registry through the use of the docker manifest inspect command


- **Validate Static Tests Site Values against Built Chart**, runs the following tests
  - Is used to ensure the schema within the built chart passes against the site values in the
Validate Static Tests area of the oss-integration-ci repo.
  - It performs this check by executing a
  ```
    helm template <APP NAME> -f site_values.yaml
  ```
  - The schema within the Built chart should pass.
  - All Helm Chart Validator site values are located in the following directory structure in this repo, see
  testsuite/common/helm-chart-validator/\<APP NAME>.


- **Run App validator Static Tests**, runs the following tests.

  >> **Note:** If your application is exempted from one of these tests please see the following section, [Skip Test](#skip-tests)
on how to add your application to the skip lists. ( Note: All code snippets referenced below can be seen
  [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/etc/testsuite/helm-chart-validator/) )

  - test docker image versions
    - This module contains test cases to verify the minimum docker image version that is used.
    - This is currently set to check for the keycloak-client image version only.
  - test openshift static tests
    - Has a number of tests included ( Note: More info on Openshift test can be seen [here](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/EO+on+Openshift+-+Security+Context+Constraints+Alignment+-+Phase+1) )
      - Test to ensure all Network Policies have an open port for an egress connection
        - Ensures that each Network Policy contains a pod selector tag and an egress connection
          ```
              if helm_template_object.does_network_policy_have_an_egress_open_connection (network_policy=network_policy_spec)
          ```
      - Test To Ensure all Containers With "Securitycontext" has "runAsNonRoot" set
        - Ensures that there is a runAsNonRoot set with appropriate permission associated with each security context
      set for pods and containers.
          ```
            assert isinstance(resulting_security_context.get('runAsNonRoot', None), bool)
          ```
  - test security vulnerabilities
    - Test that NodePort is not used in the template.type of all necessary resources
    ```
      helm_template_object = HelmTemplate("Appication Tar File", "Values file")
      service_types = helm_template_object.get_values_with_a_specific_path("spec.type")
      @pytest.mark.parametrize(('template', 'kind', 'service_type'), service_types)
      def test_nodeport_is_not_used_in_service_exposure(template, kind, service_type):
        assert 'NodePort' not in service_type
    ```
    - test validate pull secret and registry
        - Test ZYPPER Commands Are Not Used in the containers
          - Ensures that zypper is not used in the template.spec.containers of all necessary resources.
              ```
                assert 'zypper' not in str(container)
              ```
  - Test Service Mesh Static Tests
    - Has a number of tests included
      - Test Service Mesh Virtual Service Export To
        - The VirtualService shall be configured to export configuration only to the CNF/CNA namespace. The field spec.exportTo shall be hardcoded to a single entry, which is set to ".".
          ```
            if 'exportTo' in spec and spec['exportTo'] and len(spec['exportTo']) == 1 and spec['exportTo'][0] == '.':
                return True
          ```
      - Test Service Mesh Destination Rule Export To
        -  The DestinationRule shall be configured to export configuration only to the CNF/CNA namespace. The field spec.exportTo shall be hardcoded to a single entry, which is set to ".".
          ```
            if 'exportTo' in spec and spec['exportTo'] and len(spec['exportTo']) == 1 and spec['exportTo'][0] == '.':
                return True
          ```
      - Test Service Mesh Service Entry Export To
        - The ServiceEntry shall be configured to export configuration only to the CNF/CNA namespace. The field spec.exportTo shall be hardcoded to a single entry, which is set to ".".
          ```
            if 'exportTo' in spec and spec['exportTo'] and len(spec['exportTo']) == 1 and spec['exportTo'][0] == '.':
                return True
          ```
      - Test Service Mesh Ingress Gateway Hosts
        - Service mesh custom object for Ingress Gateway shall be configured to limit host configuration to services in the CNF/CNA namespace. The field spec.servers.hosts  shall be set to allow hosts only in the CNF/CNA namespace, i.e. SHALL include for namespace the "." for representing the current namespace only. In case all hosts to be exposed are not known it can be set to "./*".
            ```
              if 'servers' in spec and spec['servers']:
                  for item_server in spec['servers']:
                      if 'hosts' in item_server and item_server['hosts']:
                          for item_host in item_server['hosts']:
                            if not item_host.startswith("./"):
                              return False
            ```
        Note: "Gateway" resources applied to the Service Mesh Egress Gateway are not in the scope of the design rule. They are automatically neglected by the Helm Chart Validator and do not need to be skipped.

- **ADP Design Rules Setup and Execution**, this is the execution of the ADP Design rule against the chart under tests, please see the following
page for more info on the ADP design rule image and rules being adhered to,
[ADP Design Rule Check Automation Status](https://eteamspace.internal.ericsson.com/display/ACD/ADP+Design+Rule+Check+Automation+Status)
  - If your application is exempted from one of these tests please see the following section, [Skip Test](#skip-tests)
on how to add your application to the skip lists. ( Note: All code snippets referenced below can be seen
  [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/etc/testsuite/helm-chart-validator/) )


### Skip Tests
An application can add a skip for a test to a skip file for any of the tests within the Helm Chart Validator Stages or ADP Design
Rules, either as a specific skip for a certain application or on a common list that will be skipped for all
applications executing this stage.

>> **Note:** Any skip/exemptions being added to any of the above files need to be pre-approved from the ODP team, please see the
following page for more details [Obtain a Design Rule Exemption](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=ODP&title=Obtain+a+Design+Rule+Exemption).

The skip lists are currently part of the oss-integration-ci code base within the following area of the
repo, [helm-chart-validator skip list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helm-chart-validator/)
and the [ADP Design Rule Option list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/adp_design_rule/)

#### Helm Chart Validator Skip Test

Inside the [helm-chart-validator skip list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helm-chart-validator/)
there is a [common_skip_list.json](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helm-chart-validator/common_skip_list.json).
This lists all the common skips. Whatever entries are in this list will be skipped for all applications. For skips for
specific application there will be a directory, named with the application name (APP NAME), that lists all the skips for that application, e.g.
[eric-oss_common_base](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/helm-chart-validator/eric-oss-common-base/) skip list

The structure of the skip for each of the tests are in the following format
```
  "<NAME_OF_THE_TEST_TO_BE_SKIPPED>": {
      "skips": [
        [["<Applciation_Name>"], ["<Template Kind To be Skipped>"], "<Description why it is exempt and JIRA Number>", "skip"]
      ],
      "runTests": true
  },
```
Note: All the test names (i.e. <NAME_OF_THE_TEST_TO_BE_SKIPPED>) can be seen
[here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/etc/testsuite/helm-chart-validator/)
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

#### ADP Design Rule Skip Test
Inside the [ADP Design Rule Option list](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/adp_design_rule/)
there is a [common_design_rule_options.txt](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/adp_design_rule/common_design_rule_options.txt),
this lists all the common rules, whatever entries are in this list will be skipped for all applications. For skips for
specific application there will be a directory, named with the application name (APP NAME), that lists all the rules for that application, e.g.
[eric-oss_common_base](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/testsuite/common/adp_design_rule/eric-oss-common-base/) skip list

The structure of a basic skip for a ADP DR can be in the following format
```
-DhelmDesignRule.config.<APP NAME>.<ADP DESIGN RULE NUMBER>=skip
```
e.g.
```
  -DhelmDesignRule.config.eric-oss-common-base.DR-D1101-800=skip
```
>>Note: For more info on the ADP Design Rule Checker see the following,
[ADP Microservice Helm Chart Design Rule Builder](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/adp-cicd/adp-helm-dr-checker/+/refs/heads/master)

To add a skip to this list please contribute the review, the exemption approval from ODP and send to Ticketmaster for
final sign off, please see the [Contributing Guide](../Contribution_Guide.md) for details.

>> **Note:** It is not possible to apply microservice-specific skips when passing an integration chart into the DR checker (as is done during the common PCR).
This means that any DR skips applied to an integration chart are applied to all microservices within that chart.
As such, any new microservices being added to an integration chart must be fully compliant with the DRs applied to that chart.

### Repo Files
The following files within the oss-integration-ci [repo](https://gerrit-gamma.gic.ericsson.se/#/admin/projects/OSS/com.ericsson.oss.aeonic/oss-integration-ci)
are used in its execution.
- ci/jenkins/files/app_test/commonAppTest.Jenkinsfile *(Main Jenkins File)*
- ci/jenkins/rulesets/ruleset2.0.yaml

### Resources

The following job is used within the Base and Product staging flows
- [Jenkins Jobs](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/OSS-Integration-Common-Testing/)

### Parameters

#### Input Parameters

The following is a list of parameters that are used within the file.

| Parameter                | Description                                                                                                                                                                                                                                                                                                                         | Default                                                                  |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| GERRIT_REFSPEC           | Gerrit refspec of the app under tests example: refs/changes/88/9999988/9 - 88 - last 2 digits of Gerrit commit number / 9999988 - is Gerrit commit number / 9 - patch number of gerrit commit                                                                                                                                       |                                                                          |
| CHART_NAME               | Comma-separated dependency helm chart name list. E.g.: eric-pm-server, eric-data-document-database-pg'. Used to find the specific chart name in the Chart.yaml to swap the correct version for the service. GERRIT_REFSPEC should be blank if using this value                                                                      |                                                                          |
| CHART_VERSION            | Comma-separated dependency helm chart version list. E.g.: 1.0.0+66, 2.3.0+57. Used to swap out the version according to the CHART_NAME specified in the Chart.yaml. GERRIT_REFSPEC should be blank if using this value                                                                                                              |                                                                          |
| CHART_REPO               | Comma-separated dependency helm chart url list. E.g.: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-1,https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-pm-2'. GERRIT_REFSPEC should be blank if using this value                                                                                                          |                                                                          |
| GIT_REPO_URL             | Gerrit https url to app git repo. Example: https://gerrit-gamma.gic.ericsson.se/adp-cicd/demo-app-release-chart                                                                                                                                                                                                                               |                                                                          |
| GERRIT_PROJECT           | Gerrit project details e.g. OSS/com.ericsson.oss/oss-common-base                                                                                                                                                                                                                                                                    |                                                                          |
| VCS_BRANCH               | Branch for the change to be pushed                                                                                                                                                                                                                                                                                                  | master                                                                   |
| CHART_PATH               | Relative path to app chart in git repo.                                                                                                                                                                                                                                                                                             |                                                                          |
| GERRIT_USER_SECRET       | Jenkins secret ID with Gerrit username and password                                                                                                                                                                                                                                                                                 |                                                                          |
| ARMDOCKER_USER_SECRET    | Jenkins secret to log onto the Docker Arm                                                                                                                                                                                                                                                                                           |                                                                          |
| HELM_REPO_CREDENTIALS_ID | Repositories.yaml file credential used for auth                                                                                                                                                                                                                                                                                     |                                                                          |
| HELM_REPO_API_TOKEN      | token to access Helm repository                                                                                                                                                                                                                                                                                                     |                                                                          |
| APP_NAME                 | Application name, this is the name of the built chart, e.g. eric-oss-common-base-0.4.2-19.tgz --> **eric-oss-common-base**                                                                                                                                                                                                          |                                                                          |
| SCHEMA_TESTS_PATH        | The path to the directory containing the positive and negative schema files                                                                                                                                                                                                                                                         | testsuite/schematests/tests                                              |
| PATH_TO_SITE_VALUES_FILE | The path including file name of the site values file for templating the chart for the static test and design rule checking. The path should start from the root of the App chart repo.                                                                                                                                              | testsuite/site_values.yaml                                               |
| FULL_CHART_SCAN          | If "true" then the whole chart with its dependencies will be scanned.                                                                                                                                                                                                                                                               | false                                                                    |
| USE_ADP_ENABLER          | Use a specific adp enabler to build the chart, two options available, adp-cihelm or adp-inca. Default adp-cihelm **Note** If using "adp-cihelm", the Functional user set within the GERRIT_USER_SECRET needs to have a email address defined in the Gerrit Profile. May need to log a Ticket with Gerrit support for it's addition. | adp-cihelm                                                               |
| TIMEOUT                  | Time to wait in seconds before the job should timeout                                                                                                                                                                                                                                                                               | 3600                                                                     |
| SUBMODULE_SYNC_TIMEOUT   | Number of seconds before the submodule sync command times out                                                                                                                                                                                                                                                                       | 60                                                                       |
| SUBMODULE_UPDATE_TIMEOUT | Number of seconds before the submodule update command times out                                                                                                                                                                                                                                                                     | 300                                                                      |
| SLAVE_LABEL              | Specify the slave label that you want the job to run on.                                                                                                                                                                                                                                                                            | evo_docker_engine                                                        |
| CI_DOCKER_IMAGE          | CI Docker image to use. Mainly used in CI Testing flows                                                                                                                                                                                                                                                                             | armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default |
| CI_REFSPEC               | Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) / 95 - last 2 digits of Gerrit commit number / 156395 - is Gerrit commit number / 1 - patch number of gerrit commit / Only to be used during testing                                                                      | refs/heads/master                                                        |
>> **Note** See the following page for more details on credential's storage, [README](Credentials_Storage.md)

#### Output File

Artifacts that will be outputted from the Jenkins Job:
- The helm-template-manifest.yaml file shows the output of the helm template command for the chart that will be used during the "Run App validator Static Tests" stage & "ADP Design Rules Setup and Execution" stage.
- The static tests report (helm-chart-validator-test-report.html) generated by the "Run App validator Static Tests" stage which shows the chart's adherence to Testsuite Static Tests.
- The image_information_list.json which showcases the images gathered in the chart during the "Validating eric-product-info images" stage.
- The design-rule-check-report.html outputs the information generated by the "ADP Design Rules Setup and Execution" stage which shows the chart's adherence to Design Rules.

## Execution options
The testing phase job for a chart may need to be executed in two different ways,
- where the testing phase is executed as part of a spinnaker flow, ie when a new microservice is being added to a chart.
- during a gerrit push, to apply a verified +1 on the code review, i.e. PCR

### Execute through a spinnaker flow
To execute within a spinnaker flow the Common testing Jenkins file needs to be created on the Jenkins server, see [Jenkins Job Configuration](#Jenkins-Job-Configuration)

If the job is created,
- Link the job to the appropriate spinnaker flow
- See the [Parameters](#Parameters) Section for an explanation on what parameters are needed for the chart under test.

### Execute Post Gerrit Push
To execute the PCR post a gerrit push, so it applies a verified +1 to the review. This is achieved by applying a second
Jenkins file to execute the common testing Jenkins file.

A second Jenkins file is needed due to the fact that Jenkins uses gerrit triggers, to execute a job. This limits the
amount of details that can be sent to Common testing Jenkins job directly, so there needs to be an extra Jenkins job
per application configured, this job will be triggered by the Gerrit event and will have the chart info preconfigured
so the correct details are sent to the common testing job.

Two Jenkins jobs are required to be created,
- Common Testing Jenkins job,
  - See the [Jenkins Job Configuration](#jenkins-job-configuration) on how to create this job, if not already created.
  - Ensure the job created matches the value given within PCR_MASTER_JOB_NAME parameter from the trigger job jenkinsfile [Application In Review PCR Testing Jenkins File](App_In_Review_Common_PCR_Testing.md), as this will be needed for the next step.
- Chart PCR Job,
  - This is the job that will get triggered by the Gerrit Event. See the following page for info on the
  [Application In Review PCR Testing Jenkins File](App_In_Review_Common_PCR_Testing.md)

  >> ** Note: The following naming convention is recommended <app_name>-PCR-From-Review e.g. eric-oss-common-base-PCR-From-Review
  - When the job is created configure the following within the **configuration** of the job.
  >> **Note:**
  > The below commands should be executed in the job configuration and permanently stored in the configuration of the job
    - **Parameters Section**
      - Add the appropriate values to the **Default Value** section in the job, that are associated to the chart under
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
  > In order for Feedback to be obtained, ensure that the user executing the job has the required permissions to apply a +1/-1 Verified within the Gerrit Access Configuration of the Chart Repository

## Minimise Precode Executions after Rebase (Optional)
>> **INFO: This is an optional step.**

This involves the updating of the Gerrit configuration, support from your Gerrit support team maybe required to execute
this step.

This update involves the ignoring of trivial rebase in gerrit. A trivial rebase in gerrit is where the new content being
added to the review has no affect on the current files in the review. This maybe where another review has been
submitted previous, its files have no affect to the files in the current review that was rebased.
The review that was submitted previously should have had its own PCR executed, so it would be a waste of time and
resources to execute the PCR again, virtually on the same code base.

There is one step to enable this feature on the repo,
- Updating Gerrit configuration. **(Support from your Gerrit support team maybe required to execute this step.)**

### Update Gerrit Configuration

>> **Note: Steps below should be executed by the gerrit Admin for the repo. Please proceed with caution. Instruction here
> are for illustration only. Ticketmaster will not take responsibility for issues caused following these instructions**
- Open the Gerrit Project page for the repo.
- Edit the config through the "Edit Config" Button
- Add the following if not already there, this will preserve the scores on the labels.
```
[label "Code-Review"]
    function = MaxWithBlock
    copyMinScore = true
    value = -2 This shall not be merged
    value = -1 I would prefer this is not merged as is
    value =  0 No score
    value = +1 Looks good to me, but someone else must approve
    value = +2 Looks good to me, approved
    copyAllScoresOnTrivialRebase = true
    copyAllScoresIfNoCodeChange = true
    defaultValue = 0
[label "Verified"]
    function = MaxWithBlock
    copyMinScore = true
    value = -1 Fails
    value =  0 No score
    value = +1 Verified
    copyAllScoresOnTrivialRebase = true
    copyAllScoresIfNoCodeChange = true
    defaultValue = 0
```
For any other label currently present add the following to them,
```
[label "XYZ"]
    copyAllScoresOnTrivialRebase = true
    copyAllScoresIfNoCodeChange = true
```
- Save the content, publish and send for review as normal (Normal PCR may fail on this type of review when triggered)

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
    * * **Advanced - Refspec:** ${CI_REFSPEC}
    * **Advanced Behaviours - Advanced Clone Behaviours:** Honor refspec on initial clone
    * **Advanced Behaviours - Advanced Clone Behaviours:** Shallow Clone - Shallow Clone depth - 1
    * **Script Path:** ci/jenkins/files/app_test/commonAppTest.Jenkinsfile
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
