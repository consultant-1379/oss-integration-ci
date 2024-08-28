# Internal CI Test Spinnaker Flow for all Jenkins files managed by Ticketmaster.

[TOC]

## Introduction

This spinnaker flow can be used to execute the pre-release tests against a review for submission to master
of the oss-integration-ci repo. To execute the flow the "Submit-To-Pipeline" needs to be clicked within the review
itself. This will trigger a Gerrit event which will kick-off the [ci-pipeline-build-and-trigger](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-build-and-trigger)
The test flow will execute all the Jenkins file against the code review.

The deployment tests are executed against the HART105 deployment. A number of namespaces that have been created
specifically for this CI flow. Please see the [lockable resources](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/CI%20Test%20TM/lockable-resources/)
for a list of the namespace created, see labels ci_test_ticketmaster & ci_test_upgrade_ticketmaster.
One Install namespace and one upgrade namespace is used per flow execution.

For deployment testing stages a purpose build helmfile, eric-ci-helmfile was created, it can be found in [artifactory](https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/eric-ci-helmfile/)

Source code for the helmfile is in the oss-integration-ci repo within internal/ci-helmfile

## Main Stages of the flow

The following steps will be executed in the spinnaker flow:
- Build Dev CI Docker image
    * This will use the Gerrit ref spec sent to flow to build the new DEV CI Docker image.
    * This image will be stored in [dev repo in arm docker](https://arm.seli.gic.ericsson.se/artifactory/docker-v2-global-local/proj-eric-oss-dev/eric-oss-ci-scripts/).
    * The image version is built up by the version in VERSION_PREFIX file in the repo and the Gerrit respec.
    * This image will be one that will be tested against in the rest of the flow.
- Notification CI Flow Test Started
    * This sends back a notification to the Gerrit review that the testing has started.
- EiffelXYZ CI Pipeline Release Main
    * This is a pipeline which executes the main pipeline for testing against a specific FEM.
    * Tests are executed against different FEMs as the agents differ on allowed permissions, when a Jenkins file may
execute on one type but not the other.
    * This pipeline executes the following steps
      - Get Latest Helmfile Version
          * This is used to get the latest helmfile version from the repo specified.
          * The Gerrit ref spec and the Dev Docker image is passed to the job to ensure it is testing against the code review.
      - Upgrade (Install Testing)
          * These steps executes an upgrade using the purpose built eric-ci-helmfile tar file.
          * The Upgrade step is a [pipeline](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-upgrade-flow-test) in itself and executes the following stages.
            (All the stages below are tested against the new dev docker image which was created and the ref spec inputted)
            * Reserves Namespace
            * Gather Env Details
            * Check Deployment Status (Cluster will have a release already deployed, so will execute the full script)
            * Upgrade using Helmfile (Executes the upgrade using the purpose built eric-ci-helmfile)
            * Upgrade using Helmfile (Fail due to prepare site values issue, version 0.0.0-1 of the
            oss-ci-helmfile has extra details in the site values to ensure an error is through to test the prepare functionality)
            * Unreserve Environment
      - Initial Install (Clean Down, Pre-deployment and Install Testing)
        * These steps executes an upgrade using the purpose built eric-ci-helmfile tar file.
          The Initial Install step is a [pipeline](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-install-flow-test) in itself and executes the following stages
          (All the stages below are tested against the new dev docker image which was created and the ref spec inputted)
            * Reserves Namespace
            * Gather Env Details
            * Clean Down Deployment (Cleans down the release(s) and the PVCs etc. and removes the namespaces)
            * Pre deployment Tests (Executes all the pre-deployment that are needed for IDUN and EO)
            * Check Deployment Status (cluster will have no releases so will test that part of the code)
            * Install using Helmfile (Executes the initial install using the purpose built eric-ci-helmfile)
            * Quarantine Environment
            * Unreserve Environment
      - CSAR Checks
        * Used for testing miscellaneous Jenkins file associated with CSARs. [LINK](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=eiffel216-ci-pipeline-csar-checks)
        * The CSAR Checks step is a [pipeline](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=eiffel216-ci-pipeline-csar-checks) in itself and executes the following stages
          (All the stages below are tested against the new dev docker image which was created and the ref spec inputted)
            * CSAR Check (Checks is there a CSAR already available)
            * CSAR Builder (Executes the CSAR Builder against an application which has a CSAR already built, final part of the upload skipped - 3 Different scenarios -> With eric-product-info, without eric-product-info and with helm template and eric-product-info)
            * CSAR Properties (Generates an artifact.properties of the CSAR build according to the helmfile inputted)
            * Mini CSAR Builder (Builds the Mini CSAR according to the helmfile inputted)
            * Helmfile CSAR Builder (Executes the Helmfile CSAR Builder against a Helmfile which has a Helmfile CSAR already built, final part of the upload skipped)
            * Check Eric Product Info Information (Tests image information passed into the Check Eric Product Information Job)
      - Helm Chart Tests
        * Used for testing miscellaneous Jenkins file associated with Helm Chart. [LINK](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-helm-chart-test)
          (All the stages below are tested against the new dev docker image which was created and the ref spec inputted)
            * Chart Common PCR (Used to execute PCR against a given chart using the Common test suite)
              * These tests are associated to the following jenkins file, see [OSS Integration Common Test](../files/Common_App_Test.md)
            * INCA Helm Chart Test - Prepare - Single package
              * These tests are associated to the following jenkins file, see [Fetch, Build, Upload Using Inca](../files/Fetch_Build_Upload_Using_Inca.md)
                * The test executes the following
                  * Generates a snapshot using the "prepare" functionality within INCA.
                  * It ensures that the correct data was added to artifact and the expected version was created.
            * INCA Helm Chart Test - Publish - Single package
              * These tests are associated to the following jenkins file, see [Fetch, Build, Upload Using Inca](../files/Fetch_Build_Upload_Using_Inca.md)
                * The test executes the following
                  * Generates a full version of the package and executes the check to see if a new package was uploaded.
                    * This job is expected to **Fail** as the version was already uploaded.
        >>  Note: The INCA "publish" functionality needs to be fully tested manually prior to release of a new INCA version.
            * Compare Latest Versions in Application (Compare Microservice Versions in the Application)
              * This test is associated to the following Jenkins file, see [Compare Latest Versions In Application](../files/Compare_Latest_Versions_In_Application.md)
      - Helmfile Tests
        * Used for testing miscellaneous Jenkins file associated with Helmfile interactions.
        * The Helmfile Tests step is a [pipeline](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-helmfile-tests) in itself and executes the following stages
          (All the stages below are tested against the new dev docker image which was created and the ref spec inputted)
            * Check For CRDs (Check for a CRD file within an application)
            * Get Microservice Info (Gets all the Microservice details from a Helmfile)
            * Get Release Info (Captures all the release details from build command when executed against Helmfile inputted)
            * INCA Helmfile tests are used to verify a new INCA version.
              * These tests are associated to the following jenkins file, see [Fetch, Build, Upload Using Inca](../files/Fetch_Build_Upload_Using_Inca.md)
                * INCA Helmfile Test - Prepare - Single package
                  * Generates a snapshot using the "prepare" functionality within INCA.
                  * It ensures that the correct data was updated in the new snapshot helmfile, by downloading the generated helmfile and ensures the correct version of the chart is referenced.
                * INCA Helmfile Test - Prepare - Multiple package
                  * Using multiple charts, it generates a snapshot using the "prepare" functionality within INCA.
                  * It ensures that the correct data was updated in the new snapshot helmfile, by downloading the generated helmfile and ensures the correct versions of the charts are referenced.
            >>  Note: The INCA "publish" functionality needs to be tested manually prior to release of a new INCA version.

### Adding a new Stage to the flow
When adding a new stage to the flow ensure a test Jenkins job is created within the appropriate TAB on the FEM.
For test executed on
- fem5s11-eiffel052 see the tab [CI Test TM](https://fem5s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/view/CI%20Test%20TM/)
- fem7s11-eiffel216 see the tab [Ticketmaster_Jobs](https://fem7s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/view/Ticketmaster_Jobs/) Internal_CI_Flow section

**The main Jenkins job should not be used in the flow as a review may change the parameters, which the main flow could
pick up, which may affect the next execution in the official release flows, i.e. PSO, App Staging, Release etc.**

A New Test Jenkins job being added to the FEM should have the following
- Naming convention starting with, "CI-Test-" e.g. "CI-Test-Common-Testing".
- Both job on each FEM should have the same naming convention.
- Ensure that the job configuration is correct, to allow the review under test to be used for the testing, see the
[Contribution Guide - Configuration Changes](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/contribution-guide.md#Configuration-Changes)]
for details

When the job is being added to the spinnaker flow at a minimum the following parameters should be set to pick up the
CI Docker image under test and the GERRIT Review under test.
* CI_DOCKER_IMAGE = ${trigger['parameters']['CI_DOCKER_IMAGE']}
* GERRIT_REFSPEC = ${trigger['parameters']['GERRIT_REFSPEC']}
>> Note: The above is just an example, there maybe variations in the naming convention of the parameters.

### Pipeline Maintenance
These flows are stored in a central repository for source-controlled Spinnaker pipelines.
The flows are stored in the following repo, [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master)
under the following directory, cicd_pipelines_parameters_and_templates/ticketmaster/internal-ci-testing-flows/.

Any changes made to the flow should be updated within this repo and sent to the Ticketmaster for review.

See the following document for more details on the use and rollout of updated flows, [oss-common-cicd-pipeline-resources](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.cicd/oss-common-cicd-pipeline-resources/+/refs/heads/master/README.md#Getting-Started).

### Resources

The following is a link to the spinnaker flow
- [ci-pipeline-release-main](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-release-main)

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
