"""Module for docker operations."""
import logging
import os
import os.path
import time
import docker

from . import errors

LOG = logging.getLogger(__name__)


def run_docker_command(image, cmd, env_list=None):
    """
    Execute a docker command.

    inputs:
        image: Docker Image to use
        cmd: Docker command to execute
        env: list of environment details
    output:
        return output from the docker command as a list
    """
    returned_output_list = []
    if not env_list:
        env_list = []
    LOG.info("Initializing docker client")
    client = docker.from_env()
    cwd = os.getcwd()
    LOG.info("Image %s, running command: %s", image, ' '.join(cmd))
    container = client.containers.run(image, ' '.join(cmd),
                                      environment=env_list,
                                      volumes=[f"{cwd}:/workdir"],
                                      working_dir='/workdir',
                                      detach=True, remove=True)
    output = container.attach(stdout=True, stream=True, logs=True)
    for byte_line in output:
        line = byte_line.decode('utf-8')
        LOG.debug(str(line))
        returned_output_list.append(line)
    return returned_output_list


# pylint: disable=too-many-locals
def run_gerrit_create_patch(bob_adp_release_auto_image,
                            git_message,
                            git_repo_local=".bob/cloned_repo",
                            gerrit_branch="master"):
    """
    Execute the create patch command from the bob-adp-release-auto enabler.

    Inputs:
        bob_adp_release_auto_image:  ADP enabler bob-adp-release-auto image to use
        git_repo_local: The location of the repo to create the gerrit patch for
        git_message: Gerrit message to attach to the review
        gerrit_branch: Gerrit branch the review should be generated on0.

    Output:
        artifact.properties: which lists a number of variables included the Gerrit details for the review.
    """
    cmd_args = ["gerrit", "create-patch",
                "--message ", "\"" + git_message + "\"", " --git-repo-local", git_repo_local,
                "--branch", gerrit_branch]
    env_list = ['--user $(id -u):$(id -g)',
                'GERRIT_USERNAME=' + os.environ['GERRIT_USERNAME'],
                'GERRIT_PASSWORD=' + os.environ['GERRIT_PASSWORD']]
    try:
        output_list = run_docker_command(bob_adp_release_auto_image, cmd_args, env_list)
        for line in output_list:
            if "Change is:" in line:
                LOG.debug("Found Review URL, Generating artifact.properties")
                url = line.split("is: ")[1].rstrip()
                change_number = url.split("/c/")[1]
                last_two_numbers = str(change_number)[-2:]
                ref_spec = "refs/changes/" + str(last_two_numbers) + "/" + str(change_number) + "/1"
                with open("gerrit_create_patch.properties", "w", encoding="utf-8") as gerrit_details_file:
                    gerrit_details_file.write("GERRIT_URL=" + url + "\n")
                    gerrit_details_file.write("GERRIT_CHANGE_NUMBER=" + change_number + "\n")
                    gerrit_details_file.write("GERRIT_REFSPEC=" + ref_spec + "\n")
                    gerrit_details_file.write("GERRIT_BRANCH=" + gerrit_branch + "\n")
                    gerrit_details_file.write("GERRIT_PATCHSET_NUMBER=1\n")
    except Exception as ex:
        raise errors.GerritError(f"Unable to create a Gerrit patch set. Exception thrown: {ex}")


def check_gerrit_review_submittable(adp_int_helm_chart_auto, gerrit_change_number, timeout):
    """
    Execute the gerrit submittable command from the adp-int-helm-chart-auto enabler.

    Inputs:
        adp_int_helm_chart_auto:  ADP enabler adp-int-helm-chart-auto image to use
        gerrit_change_number: The change number associated to the gerrit review
        timeout: Amount of time to wait for the review to become submittable i.e. it gets a +1 verified & +2 Code review

    Output:
        Check passes or fails.
    """
    cmd_args = ["gerrit", "submittable",
                "--change ", "\"" + gerrit_change_number + "\""]
    env_list = ['--user $(id -u):$(id -g)',
                'GERRIT_USERNAME=' + os.environ['GERRIT_USERNAME'],
                'GERRIT_PASSWORD=' + os.environ['GERRIT_PASSWORD']]
    max_number_of_tries = int(timeout) // 30
    attempt_number = 0
    try:
        while True:
            submittable = False
            attempt_number = attempt_number + 1
            LOG.info("Try %s of %s", attempt_number, max_number_of_tries)
            output_list = run_docker_command(adp_int_helm_chart_auto, cmd_args, env_list)
            for line in output_list:
                if "Submittable" in line:
                    LOG.info("Review is Submittable")
                    submittable = True
            if not submittable:
                LOG.debug(str(output_list))
                if attempt_number >= max_number_of_tries:
                    LOG.info("Review not submittable")
                    raise errors.GerritSubmitError("The review has not become submittable in the timeout set.")
                LOG.info("Review not submittable, sleep 30 seconds before retry.")
                time.sleep(30)
            else:
                break
    except Exception as ex:
        raise errors.GerritError(f"Issue with execution of submittable check. Exception thrown: {ex}")


def run_kubeconform(kubeconform_image, cmd):
    """
    Execute kubeconform analysis for CR file.

    Input:
        kubeconform_image: Kubeconform image to run
        cmd: Command to run within image
    """
    client = docker.from_env()
    cwd = os.getcwd()
    LOG.info("Image %s, running command: %s", kubeconform_image, cmd)
    container = client.containers.run(kubeconform_image, cmd,
                                      volumes=[f"{cwd}:{cwd}"],
                                      working_dir=f"{cwd}",
                                      stderr=True,
                                      detach=True)
    container.wait()
    out = container.logs(stdout=True, stderr=True)
    return out


# pylint: disable=broad-except
def run_am_package_manager_generate(am_pkg_mgr_image, csar_name, chart_pkg_list, include_images="false"):
    """
    Execute AM package manager to generate CSAR packages.

    Input:
        am_pkg_mgr_image: AM package manager image to run
        csar_name: Name of the CSAR package to create
        chart_pkg_list: List of helm charts to include in the CSAR
        include_images: Set to "true" if CSAR should contain image tar
    """
    LOG.info("Initializing docker client")
    client = docker.from_env()
    cmd_args = ["generate", "--name", csar_name, "--helm", ' '.join(chart_pkg_list)]
    if include_images == "false":
        cmd_args.append("--no-images")
    cwd = os.getcwd()
    LOG.info("Image %s, running command: %s", am_pkg_mgr_image, ' '.join(cmd_args))
    retry_count = 10
    while retry_count > 0:
        try:
            client.containers.run(am_pkg_mgr_image, ' '.join(cmd_args),
                                  volumes=[f"{cwd}:/workdir"], working_dir='/workdir')
            # Verify CSAR is present after generation
            if os.path.exists(os.path.join(cwd, f"{csar_name}.csar")):
                LOG.info("CSAR %s successfully created", csar_name)
                return
            raise errors.MissingCSARError("CSAR missing.")
        except Exception as ex:
            LOG.info("An error occurred in generating the CSAR:\n%s"
                     "\nSleeping for 30 seconds before retrying the operation...", str(ex))
        finally:
            time.sleep(30)
            retry_count -= 1
    # Unable to build CSAR after retries, so error out
    raise errors.MissingCSARError(f"CSAR {csar_name} failed to generate")


def cleaning_up_workspace_from_properties_file(property_file):
    """
    Clean up workspace to be left with CSARs and chart TGZ.

    Input:
        property_file: Property file with name-version=<CSV list of charts to include> entries

    Output:
        Clean up workspace to be left with CSARs and chart TGZ.
    """
    cleanup_charts_list = []

    with open(property_file, "r", encoding="utf-8") as am_pkg_mgr_properties_file:
        am_pkg_mgr_properties = am_pkg_mgr_properties_file.readlines()
        for prop in am_pkg_mgr_properties:
            LOG.info("Found property entry: %s", prop)
            property_entry = prop.split("=")
            if len(property_entry) <= 1:
                raise errors.InvalidPropertyError(f"Invalid property found: {prop}")
            csar_chart_content_list = property_entry[1].strip().split(",")

            for chart_pkg_file in csar_chart_content_list:
                if chart_pkg_file not in cleanup_charts_list and os.path.exists(chart_pkg_file):
                    cleanup_charts_list.append(chart_pkg_file)

    for chart_pkg_file in cleanup_charts_list:
        if "helmfile" in chart_pkg_file:
            LOG.info("Retaining %s", chart_pkg_file)
        else:
            LOG.info("Deleting %s", chart_pkg_file)
            os.remove(chart_pkg_file)
