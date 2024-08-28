Contribution Model
=============================

Teams are welcome to contribute to this code base.

The goal of having these guidelines in place is to maintain a high level of code
quality and maintainability, while facilitating teams to
contribute to the code base.

When contributing to this repository, please first discuss the change you wish
to make, either by registering a [TicketMaster support ticket](
https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091)
or via a mail to the [guardians](#Project-Guardians) before making a change.

The following is a set of guidelines for contributing to this repo.
These are mostly guidelines, not rules. Use your best judgment, and
feel free to propose changes to this document.

Any file being changed in this repo should following these guidelines.

## Table of Contents

[TOC]

## Project Guardians

The guardians are the maintainer of this repo. They are responsible to guide the
contributors and review the submitted patches.

-  Team : Ticketmaster (<PDLTICKETM@pdl.internal.ericsson.com>)

## Development Environment prerequisites

The files within the repo are mainly Jenkins file so you must have access to your own Jenkins server
where you will have permission to create new Jenkins jobs.

## How can I use this repository?

This repository contains the source code for the majority of the IDUN CI/CD scripts.
Service including deployment, purge, csar building, environment reservation,
CI site values, documentation etc.

If you want to fix a bug or just want to experiment with adding a feature,
you'll want to clone the repo into your environment using a local copy of the
project's source.

You can start cloning the GIT repository to get your local copy:

```text
git clone ssh://<userid>@gerrit-gamma.gic.ericsson.se:29418/OSS/com.ericsson.oss.eiae/eiae-helmfile
```

Once you have your local copy,
- CI/CD Jenkins File can be found in ./ci/jenkins/files/
- CI/CD Site values files can be found in ./site-values/ci/
- CI/CD CSAR Build Site Values file per application can be fond in ./site-values/csar-build

If you are satisfied with your change and want to submit for review,
create a new git commit and then push it with the following:

```text
git push origin HEAD:refs/for/master
```

## How Can I Test A Change on a Jenkins File Without Affecting the Master Branch?

> **Note:** Prerequisite - In order to test a change in a Jenkins file, the first execution needs to take place prior to the below changes

### Gerrit_Refspec and Fetch_Head Parameters

The GERRIT_REFSPEC parameter will allow for the ability to test a Jenkinsfile on the master branch (refs/heads/master) or via a specific commit (refs/changes/95/156395/1).

The specific commit can be found through the Checkout function within the Downloads dropdown of the specific commit:
- 95 on the commit represents the last two digits of the Gerrit Number
- 156395 on the commit represents the Gerrit Number
- 1 on the commit represents patch number on the Gerrit Commit

The FETCH_HEAD parameter in Git is a short-lived reference that provides the ability to point to the latest commit on the current branch (or specific commit).

### Configuration Changes

In order to test a change on the Jenkins file specified above, the following changes will have to be made after the first execution:

- Within the "Pipeline Section" of the Jenkins Job Configuration set the following
    * **Branches to build:** FETCH_HEAD
    * **Within Advanced, set Refspec:** ${GERRIT_REFSPEC}
    * **Additional Behaviours --> Advanced clone behaviours**
      * Uncheck: Fetch tags
      * Check: Honor refspec on initial clone
      * Check: Shallow clone depth --depth 1

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for a file within this repo.
Following these guidelines helps maintainers and the community understand your
report, reproduce the behaviour, and find related reports.

Before creating bug reports, please check
[this JIRA list](https://jira-oss.seli.wh.rnd.internal.ericsson.com/secure/RapidBoard.jspa?rapidView=7258&projectKey=IDUN&view=planning&selectedIssue=IDUN-4091&issueLimit=100)
as you might find out that you don't need to create one. When you are creating a bug report,
 please [include as many details as possible](#How-Do-I-Submit-A-Good_Bug-Report).

> **Note:** If you find a **Closed** issue that seems like it is the same
thing that you're experiencing, open a new issue and include a link to
the original issue in the body of your new one.

#### Before Submitting A Bug Report

- **Check the files documentation, all docs can be found listed on the main repo [page](link).**
You might be able to find the cause of the problem and fix things yourself.
- **Check the [FAQs](FAQ.md)** page, for a list of common questions and problems.
- **Perform a search in [this JIRA list](https://jira-oss.seli.wh.rnd.internal.ericsson.com/secure/RapidBoard.jspa?rapidView=7258&projectKey=IDUN&view=planning&selectedIssue=IDUN-4091&issueLimit=100)**
to see if the problem has already been reported. If it has and the issue is still open,
add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Bug Report?

Use the following JIRA template to register a bug, [JIRA template](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091).
 Create an issue, ensure to populate as much detail in the template as possible.

Explain the problem and include additional details to help maintainers reproduce
the problem, Ensure the following points are cover in the JIRA:

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as much
detail as possible.
- **What version of the helmfile is being deployed.**
- **What version of the deployment manager was used to execute the deployment.**
- **Attach the site values used to execute the deployment.**
- **Attach the deployment logs.**
- **If Documentation is being used to executed the deployment, include it's details.**
- **Include details about your configuration and environment** e.g. "is the cluster CaaS or AKS or AWS or something else.
- **Describe the behaviour you observed** and point out what exactly is
the problem with that behaviour.
- **Explain which behaviour you expected to see instead and why.**
- **If the problem wasn't triggered by a specific action**, describe what you
were doing before the problem happened.

### Suggesting Features

This section guides you through submitting an enhancement suggestion, including
completely new features and minor improvements to existing functionality.
Following these guidelines helps maintainers and the community understand your
suggestion and find related suggestions.

Before creating feature suggestions, please check
[this JIRA list](https://jira-oss.seli.wh.rnd.internal.ericsson.com/secure/RapidBoard.jspa?rapidView=7258&projectKey=IDUN&view=planning&selectedIssue=IDUN-4091&issueLimit=100)
 as you might find out that you don't need to create one. When you are creating a feature suggestion,
please [include as much detail as possible](#How-Do-I-Submit-A-Good_Feature-Suggestion).

#### Before Submitting A Feature Suggestion

- **Check the files documentation, all docs can be found listed on the main repo
[page](../README.md).**
- **Perform a search in [this JIRA list](https://jira-oss.seli.wh.rnd.internal.ericsson.com/secure/RapidBoard.jspa?rapidView=7258&projectKey=IDUN&view=planning&selectedIssue=IDUN-4091&issueLimit=100)**
to see if the feature has already been suggested. If it has, add a comment to the existing ticket instead of
opening a new one.

#### How Do I Submit A (Good) Feature Suggestion?

Use the following ticketmaster JIRA Support template to register a new feature suggestion,
[bug/support template](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-4091).

Create a support request on it providing the following information:

- **Use a clear and descriptive title** for the issue to identify
the suggestion.
- **Provide a step-by-step description of the suggested feature** in as much
detail as possible.
- **Explain why this feature would be useful** to most users of the service.

**Note: A design analysis may be requested by the [guardians](#Project-Guardians)
once this ticket has been submitted and reviewed.**

### Overview of how the eric-oss-ci-scripts image is used within CI

The Ticketmaster team are owners of the eric-oss-ci-scripts image, which is a command-line tool packaged as a Docker image that is used in a variety of Jenkins jobs (see [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/) for a list of these jobs). A more detailed overview of how this image functions in the CI (with examples) and how to test it is provided [here](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/Contributing+to+the+eric-oss-ci-scripts+image). Any changes this document should be reflected in the attached Confluence page and vice versa.

**CLI commands**

There are a number of Python modules within the eric-oss-ci-scripts image that contain the various CLI commands:
- **confluence_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/confluence_executor.py). This file contains all the CLI commands related to working with Confluence and Jira.
- **crd_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/crd_executor.py). This file contains all the CLI commands related to working with CRDs.
- **csar_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/csar_executor.py). This file contains all the CLI commands related to building and working with CSARs.
- **gerrit_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/gerrit_executor.py). This file contains all the CLI commands related to gerrit commands.
- **helm_chart_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/helm_chart_executor.py). This file contains all the CLI commands related to working with helm chart data.
- **helmfile_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/helmfile_executor.py). This file contains all the CLI commands related to working with helmfile data.
- **kubectl_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/kubectl_executor.py). This file contains all the CLI commands related to using kubectl commands.
- **site_values_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/site_values_executor.py). This file contains all the CLI commands related to working with the site values file.
- **utils_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/utils_executor.py). This file contains a variety of utility and unrelated single-use commands.
- **pre_code_review_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/pre_code_review_executor.py). This file contains the CLI commands used for the centralised PCR job, such as running static and schema tests.
- **cihelm_executor.py** - this file can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/bin/cihelm_executor.py). This file contains the CLI commands used for cihelm, such as fetching and packaging charts.

All of the possible parameters that can be passed into the various CLI commands are outlined at the top of each of these files. Each of the CLI commands are written as Python functions within these files, which can be identified by the @cli.command() decorator above each function. Each of the parameters needed for the CLI command are also included as decorators above the function.
Within the CLI command function, a function is called from a different module to perform the necessary task.

The code containing the actual functionality is stored in different modules within the [lib directory](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/lib/).
Every function is logically grouped within modules based on their intended functionality. For example, functions interacting with CSARs are contained within the csar.py module and general-purpose functions (such as the extract_tar_file_and_archive_base_directory function) are contained in the utils.py module.

**Calling CLI Commands from the ruleset**

In order to call the CLI commands contained within the various executor python modules from a Jenkinsfile, a rule needs to be created within the ruleset. The ruleset can be found at [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/rulesets/ruleset2.0.yaml).
Each key nested within the "rules" key of the ruleset represents a different rule; each rule contains commands to implement different functionality. If new functionality is added to the eric-oss-ci-scripts image, the rule to call this functionality must contain the following values:
- A task name representative of the functionality being implemented
- The name of the docker image (e.g., armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:latest)
- A list of Docker flags
- A reference to the appropriate executor module and CLI command, followed by the parameters

When this task is called from the Jenkinsfile, the different keys are combined to form a full CLI command using the Docker flags and parameters specified.

**Calling the ruleset from a Jenkinsfile**

To use the CLI commands contained within the ruleset, the bob submodule needs to be referenced, along with the rule name and the desired task within that rule.
If only the rule name is called from the Jenkinsfile, every task within that rule is executed. For example, a rule with the name "helmfile" and a task of the name "extract-helmfile" would need to call "{bob} helmfile:extract-helmfile".

**Dockerfile**

The Dockerfile of the eric-oss-ci-scripts image installs numerous executables as part of the image, including kubectl, helm, and helmfile. As such, commands associated with these executables can be run within the eric-oss-ci-scripts image.
If new executables need to be added to the image, the binary file of the executable needs to be added to the /usr/bin/ directory as part of the Dockerfile. The Dockerfile can be found [here](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/Dockerfile).

### Overview of how to test the image

**Testing new functionality manually**

It is expected that any new functionality delivered into the eric-oss-ci-scripts has been manually tested, both locally and in the Jenkinsfile where the new functionality is being used.
An overview of how to build the image locally is provided within the README file of the image: [README](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/README.md).
An overview of how to test new functionality within a Jenskinsfile is provided within the contribution guide of the oss-integration-ci repository: [contribution-guide](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/Contribution_Guide.md).

**PCR testing**

As part of the PCR job for the oss-integration-ci repository, Pylint is used to ensure the codebase within the image adheres to the recommended style.
If new code violates this coding style, the image build will fail and the code will need to be formatted accordingly. However, if new code violates the Pylint rules for reasons that are necessary for the code to function (e.g., a function with a large number of arguments), this rule can be overridden by entering "pylint: disable=too-many-arguments" as a comment above the offending function.
Additionally, each function written in the eric-oss-ci-scripts image requies a doc string outlining the purpose of the function and a summary of the parameters, which is enforced by pydocstyle.

**Internal CI testing pipeline**

Every change to the codebase of the eric-oss-ci-scripts image is required to pass the ci-pipeline-release-main Spinnaker flow, which can be found [here](https://spinnaker.rnd.gic.ericsson.se/#/applications/ticketmaster-cicd/executions?pipeline=ci-pipeline-release-main).
This Spinnaker flow runs the changes made to the codebase through each Jenkinsfile contained within the oss-integration-ci repo to ensure the changes do not break the current functionality.
To pass a code change to this Spinnaker flow, click on the "Reply..." button on the Gerrit change and tick the "Submit-to-Pipeline" option. This will run the ci-pipeline-release-main Spinnaker flow with the changes made.
See the following page for more details on the [Internal CI Test Flow](flows/Internal_CI_Test_Flow.md)

**Note** - Any new Jenkinsfiles added to the oss-integration-ci repo will need to be added to the ci-pipeline-release-main Spinnaker flow so they can be tested as part of this flow.

**Unit testing**

All new code functionality added to the eric-oss-ci-scripts image requires unit testing. These unit tests are executed as part of the image build; if code coverage falls below the accepted percentage of code coverage, the image build will fail and the new image will not be released.

Unit testing for the eric-oss-ci-scripts image is done using the pytest and click libraries. Each unit test is written as a function within the .py files within the [tests](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/ci/jenkins/scripts/python-ci-scripts/src/tests/) directory. Each CLI command requires its own .py file for dedicated unit tests; the naming convention for these tests files is "test_<executor_name>_executor_<cli_command_name>.py". For example, the .py file for the extract_tar_file CLI command would be called "test_utils_executor_extract_tar_file.py". Each function within these files must begin with "test" in order to run as a unit test during the image build.

The unit tests for the eric-oss-ci-scripts image use the CliRunner class from the click library. The CliRunner executes the CLI commands in isolation and captures the output and exit status for testing purposes. The monkeypatch and caplog fixtures of the pytests class are also regularly used in these unit tests to mock function behaviour and capture/test the output of the CLI commands, respectively.

### Submitting Contributions for Review, Bug or new feature

**Overview on adding new functionality**

If existing functionality needs to be edited, then the code within the existing functions can be edited accordingly. However, if adding new functionality to the image, any new functions will need to be added to the .py files contained within the ci/jenkins/scripts/python-ci-scripts/lib directory within the oss-integration-ci repository (ci/jenkins/scripts/python-ci-scripts/src/lib - OSS/com.ericsson.oss.aeonic/oss-integration-ci - Gitiles).
Any new functions should be added to the .py file where similar functions are grouped (e.g., functions operating on CSARs should be added to the csar.py module). Also, new functions should be as generic as possible for the purpose of reusability.

Once any new functions have been added, a new CLI command will need to be added to the appropriate executor.py file within the ci/jenkins/scripts/python-ci-scripts/bin directory (ci/jenkins/scripts/python-ci-scripts/src/bin - OSS/com.ericsson.oss.aeonic/oss-integration-ci - Gitiles).
Any parameters for the CLI command that are not already available at the top of this file will also need to be added.

After adding the new CLI command, a rule will need to be created in the ruleset to call the command. This command can then be called within the Jenkinsfile where the functionality is required.

**Note: We are only accepting new features into this repository through Python scripts**
- We are no longer accepting Shell scripts within this repository
- Any new features must be submitted through Python scripts

**Overview on adding new documentation**

Any documentation updates or additions should be made in the relevant area in [Documentation](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/)

The naming convention for documentation is as follows:
- Each word in the title of the document begins with a capital letter
- Each word in the document is separated by an underscore e.g. Contribution_Guide.md
- Hyphens/dashes can be used where applicable
  - If the document title references a technical component such as a secret, e.g. Eric-Sec-Access-Mgmt-Creds_Secret.md
  - For punctuation e.g. EVNFM_Pre-Deployment.md

Updates to the functionality of a Jenkinsfile should be reflected in the existing relevant Jenkinsfile documentation.
If a new Jenkinsfile is being added to execute the new functionality, then the appropriate Jenkinsfile documentation
must also be added.
Additions to Jenkinsfile documentation should be made in the [Jenkinsfiles Documentation](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/files/)

Internally, Ticketmaster document CI flows in [Flows](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/docs/flows)

**Step 1: After implementation and testing is complete Send for code review**

-   Review should follow the Code Review [Guidelines](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/HP+Code+Review+Guidelines).
-   Reviews should be kept small (No more than 300 lines of code per review).
-   Reviews should be submitted independently(No parent code reviews).
-   Reviews should be submitted to Microsoft Teams [Code Review Channel](https://teams.microsoft.com/l/channel/19%3a24a63aa23b484b8092251565822c18f0%40thread.skype/Code%2520Review%2520Requests?groupId=1483901a-b5c4-445a-b707-aa7a5d0c1b4c&tenantId=92e84ceb-fbfd-47ab-be52-080c6b87953f).
    If Microsoft Teams is not available, please register a JIRA for the review using the following [template](https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/IDUN-5065).
    **Note** Reviews coming from teams should have a +1 from your team itself before the review is posted and passing the CI Test Flow see, [Internal-CI-Test-Flow](./flows/Internal_CI_Test_Flow.md) for more details on its execution.

-   Code must not break any pipelines or existing tests.
-   New functionality needs to include tests if applicable.

**Step 2: Code is merged**

- The reviewer who gives the +2 will merge the code.
- The reviewer will follow the commit through the pipeline.

### Override files
This repository contains a number of override files within the [site-values](https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.aeonic/oss-integration-ci/+/refs/heads/master/site-values/) directory. The Ticketmaster team are not responsible for these files; these files are overseen by the areas that use these files.

A more detailed overview of override files can be found [here](https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/DGBase/Overview+of+override+files).

