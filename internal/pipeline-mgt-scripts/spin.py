"""Module for spin operations."""
import logging
import os
import subprocess
import time
import json
import csv
import oyaml as yaml
import utils
import errors

LOG = logging.getLogger(__name__)
SPIN = "/usr/local/bin/spin"
SPIN_CONFIG_FILE = "/tmp/.spin.config"
SPIN_DEFAULT_URL = "https://spinnaker-api.rnd.gic.ericsson.se"


def run_spin_command(config_file_path, *spin_args):
    """
    Execute a spin command.

    Input:
        config_file_path: File path to spin config
        *spin_args: List of spin command arguments

    Returns
    -------
        Command object

    """
    command_and_args_list = [SPIN, '--config', config_file_path]
    command_and_args_list.extend(spin_args)
    command = utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command


def run_spin_command_with_retry(config_file_path, retry_count, retry_sleep_in_s, *kubectl_args):
    """
    Execute a kubectl command with a retry on error code returned.

    Input:
        config_file_path: File path to spin config
        retry_count: Number of times to retry a failed operation
        retry_sleep_in_s: Number of seconds to sleep in between retries
        *kubectl_args: List of kubectl command arguments

    Returns
    -------
        Command object

    """
    # Set defaults
    if isinstance(retry_count, int) is False or retry_count < 1:
        retry_count = 1
    if isinstance(retry_sleep_in_s, int) is False or retry_sleep_in_s < 1:
        retry_sleep_in_s = 1
    counter = 0
    new_args = []
    new_args.extend(kubectl_args)
    while counter < retry_count:
        LOG.debug("Spin command: %s", ' '.join(new_args))
        command = run_spin_command(config_file_path, *new_args)
        if command.returncode == 0:
            break
        time.sleep(retry_sleep_in_s)
        counter += 1
    return command


def setup_spin_config(spinconfig_file):
    """
    Create Spin configuration file if it doesn't exist.

    Input:
        spinconfig_file: File path to spin config

    Output:
        Creates Spin config file if required
    """
    if os.path.isfile(spinconfig_file):
        return
    if 'SPIN_USERNAME' not in os.environ:
        raise errors.MissingEnvVarError("Missing environment variable SPIN_USERNAME")
    if 'SPIN_PASSWORD' not in os.environ:
        raise errors.MissingEnvVarError("Missing environment variable SPIN_PASSWORD")
    output_dict = {
        'gate': {
            'endpoint': SPIN_DEFAULT_URL
        },
        'auth': {
            'enabled': True,
            'basic': {
                'username': os.environ.get('SPIN_USERNAME'),
                'password': os.environ.get('SPIN_PASSWORD')
            }
        }
    }
    with open(spinconfig_file, "w", encoding="utf-8") as spin_output_yaml_file:
        yaml.dump(output_dict, spin_output_yaml_file)


def get_app_details(spinconfig_file, app_name):
    """
    Get application details JSON.

    Input:
        spinconfig_file: File path to spin config
        app_name: Reference application name

    Output:
        Application details in JSON format
    """
    spin_get_app_details = run_spin_command(spinconfig_file, 'application', 'get', app_name)
    if spin_get_app_details.returncode == 0:
        return json.loads(spin_get_app_details.stdout.decode('utf-8'))
    LOG.error(spin_get_app_details.stderr.decode('utf-8'))
    raise errors.SpinCLIError(f"Error getting details for app {app_name}")


def get_apps_by_keyword(keyword):
    """
    List applications by keyword.

    Input:
        keyword: Sub-string to match within an app name

    Output:
        List of application names that contain a passed-in keyword
    """
    spin_get_apps = run_spin_command(SPIN_CONFIG_FILE, 'application', 'list')
    return_app_list = []
    if spin_get_apps.returncode == 0:
        app_list_data = json.loads(spin_get_apps.stdout.decode('utf-8'))
        for app_entry in app_list_data:
            if keyword in app_entry["name"]:
                return_app_list.append(app_entry["name"])
        return return_app_list
    LOG.error(spin_get_apps.stderr.decode('utf-8'))
    raise errors.SpinCLIError("Error listing apps")


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
def sync_app_banner_msg(app_list, banner_text, bg_color, text_color, enabled, skip, delete):  # noqa: C901
    """
    Sync app banner message updates.

    Input:
        spinconfig_file: File path to spin config
        app_list: Reference application name list (CSV)
        banner_text: Message to include in banner
        bg_color: Background color for the banner
        text_color: Banner message text color
        enabled: Sets the enabled flag for the banner (active if true, disabled by default)
        skip: Skips the update if set to true
        delete: Deletes the banner message if found in the app

    Output:
        Updated or removed application banner message, if skip isn't set
    """
    setup_spin_config(SPIN_CONFIG_FILE)
    apps = [app.strip() for app in app_list.split(" ")]
    # Translate common names and enabled flag
    bg_color = f"var(--color-{bg_color.strip()})"
    text_color = f"var(--color-text-{text_color.strip()})"
    enabled = utils.str_to_bool(enabled)
    skip = utils.str_to_bool(skip)
    delete = utils.str_to_bool(delete)
    for app_name in apps:
        app_name = app_name.strip()
        if not app_name:
            continue
        # Check for app list expansion
        if "ALL_" in app_name:
            expanded_app_list = get_apps_by_keyword(app_name.replace("ALL_", ""))
            apps.extend(expanded_app_list)
            LOG.info("Expanded list of apps for entry %s: %s", app_name, expanded_app_list)
            continue
        # Special case to just log the potential update but take no action
        # on the application -- mostly for placeholders in the CSV
        if skip:
            LOG.info("Skipping banner message '%s' update for application %s", banner_text, app_name)
            continue
        if delete:
            LOG.info("If found, removing banner message '%s' from app %s", banner_text, app_name)
        else:
            LOG.info("Updating banner message '%s' for application %s", banner_text, app_name)
        app_details_json = get_app_details(SPIN_CONFIG_FILE, app_name)
        banner_list = []
        action_taken = False
        if 'customBanners' not in app_details_json:
            app_details_json['customBanners'] = []
        else:
            # Replace properties for an existing banner entry that
            # matches the text
            for banner in app_details_json['customBanners']:
                LOG.info("Found existing banner message '%s'", banner['text'])
                # Restrict single banner message based on text
                banner_list_with_text = list(filter(lambda x: (x['text'] == banner_text), banner_list))
                if banner['text'] == banner_text and delete:
                    LOG.info("Removing found banner '%s' from app %s", banner_text, app_name)
                    action_taken = True
                    continue
                if banner['text'] == banner_text and not banner_list_with_text:
                    if banner['backgroundColor'] != bg_color or \
                       banner['textColor'] != text_color or \
                       banner['enabled'] != enabled:
                        LOG.info("Updating EXISTING banner with new properties...")
                        banner['backgroundColor'] = bg_color
                        banner['textColor'] = text_color
                        banner['enabled'] = enabled
                        banner_list.append(banner)
                        action_taken = True
                    else:
                        LOG.info("Skipping EXISTING banner update as properties are unchanged...")
                        # Just re-add the existing banner, no updates
                        banner_list.append(banner)
                else:
                    if enabled and banner['enabled']:
                        # Disable the previous banner to mitigate the bug
                        # with Spinnaker CLI update where multiple banners
                        # can be enabled at once...
                        banner['enabled'] = False
                        action_taken = True
                        LOG.info("Disabling an existing banner...")
                    # Just re-add the existing banner, no updates
                    banner_list.append(banner)
        banner_list_with_text = list(filter(lambda x: (x['text'] == banner_text), banner_list))
        if not banner_list_with_text and not delete:
            LOG.info("Adding NEW banner...")
            banner_entry = {}
            banner_entry['backgroundColor'] = bg_color
            banner_entry['text'] = banner_text
            banner_entry['textColor'] = text_color
            banner_entry['enabled'] = enabled
            banner_list.append(banner_entry)
            action_taken = True
        if action_taken:
            # Add entries back to banner list
            app_details_json['customBanners'] = banner_list
            with open("./app_update.json", "w", encoding="utf-8") as updated_app_details_json_file:
                updated_app_details_json_file.write(json.dumps(app_details_json, indent=4))
            spin_save_app = run_spin_command(SPIN_CONFIG_FILE, 'application', 'save', '--file', "./app_update.json")
            spin_save_app_output = utils.join_command_stdout_and_stderr(spin_save_app)
            LOG.info("Output: %s", spin_save_app_output)
            if "Application save succeeded" in spin_save_app_output:
                LOG.info("Banner added to app %s successfully", app_name)
            else:
                raise errors.SpinCLIError(f"Unable to update app {app_name}")
        else:
            LOG.info("No updates found for app %s, save skipped...", app_name)


def sync_banner_csv(csv_file):
    """
    Update banners using CSV file reference.

    Input:
        csv_file: File path to CSV definitions

    Output:
        Updates banners based on CSV input
    """
    with open(csv_file, 'r', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        next(reader)
        for csv_row in reader:
            sync_app_banner_msg(*csv_row)
