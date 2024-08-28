"""Module to manage site-values for helmfile."""
import copy
import logging
import oyaml as yaml  # pip install oyaml

from . import utils

LOG = logging.getLogger(__name__)
yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
yaml.add_representer(str, utils.str_rep, Dumper=yaml.SafeDumper)


def set_deployment_tags(state_values_file, deployment_tag_list):
    """
    Set all application tags to true in state values file.

    Input:
        state_values_file: State values yaml file for tag updates
        deployment_tag_list: Space-separated list of tags to enable

    Output:
        Writes updated yaml to state_values_file after enabling specified tags
    """
    LOG.info('Set true for such tags: "%s"', deployment_tag_list)

    with open(state_values_file, 'r', encoding="utf-8") as stream:
        parsed_yaml = yaml.safe_load(stream)

    deployment_tag_list = deployment_tag_list.split(' ')

    if "None" in deployment_tag_list:
        if len(deployment_tag_list) > 1:
            raise Exception(f'There should be no other tags if "None" is set: {" ".join(deployment_tag_list)}')
        LOG.info("No tags have been set. Only base applications will be installed...")
        return

    for tag in deployment_tag_list:
        if tag in parsed_yaml['tags']:
            parsed_yaml['tags'][tag] = True
        else:
            raise Exception(f'There is no such tag "{tag}" in yaml file')

    with open(state_values_file, 'w', encoding="utf-8") as yaml_file:
        yaml.safe_dump(parsed_yaml, yaml_file, allow_unicode=True)


def obfuscate_registry_password(state_values_file):
    """
    Replace cleartext password in a state values file with obfuscated string.

    Input:
        state_values_file: State values file to update

    Output:
        Write updated yaml to state_values_file after replacing registry password
    """
    with open(state_values_file, 'r', encoding="utf-8") as stream:
        parsed_yaml = yaml.safe_load(stream)

    LOG.info('Obfuscating registry passwords in state values file')

    if 'password' in parsed_yaml['global']['registry']:
        parsed_yaml['global']['registry']['password'] = '******'
    else:
        LOG.info("No registry password to obfuscate")
        return

    obfuscated_parsed_yaml = copy.deepcopy(parsed_yaml)
    obfuscated_parsed_yaml = obfuscate_site_values_passwords(obfuscated_parsed_yaml)

    LOG.info('Parsed yaml file:\n %s', yaml.safe_dump(obfuscated_parsed_yaml))

    with open(state_values_file, 'w', encoding="utf-8") as yaml_file:
        yaml.safe_dump(parsed_yaml, yaml_file, allow_unicode=True)


def obfuscate_site_values_passwords(state_values_file):
    """
    Replace cleartext password in a state values file with obfuscated string.

    Input:
        state_values_file: State values file to update

    Output:
        Return updated yaml with obfuscated password
    """
    for key, value in state_values_file.items():
        if key == "password" and value != '******':
            state_values_file["password"] = '******'
        else:
            if isinstance(value, dict):
                state_values_file[key] = obfuscate_site_values_passwords(value)
    return state_values_file


def find_shared_nested_value(values_file, parent_key, desired_value, parent_key_found=False):
    """
    Find a shared nested value within a site values file.

    Input:
        values_file: The site values file containing the desired value
        parent_key: The parent key containing the desired value (e.g., service-mesh-ingress-gateway)
        desired_value: The key containing the desired value (e.g., loadBalancerIP)
        parent_key_found: A value used to redirect the function once the parent key has been found

    Output:
        Returns the value associated with the desired key
    """
    for key, value in values_file.items():
        if isinstance(value, dict) and not parent_key_found:
            if key == parent_key:
                result = find_shared_nested_value(value, parent_key, desired_value, parent_key_found=True)
                if result is not None:
                    return result
            else:
                result = find_shared_nested_value(value, parent_key, desired_value, parent_key_found=False)
                if result is not None:
                    return result
        elif isinstance(value, dict) and parent_key_found:
            result = find_shared_nested_value(value, parent_key, desired_value, parent_key_found=True)
            if result is not None:
                return result
        elif parent_key_found and key == desired_value:
            return value
        else:
            continue
    return None


def create_site_values_file(key_value_list, output_yaml):
    """
    Create a new site values file from a list of keys.

    Input:
        key_value_list: A comma separated list of nested yaml dictionary keys
        output_yaml: File path for the new site values file

    Output:
        Writes merged dictionary to new yaml file.
    """
    yaml_dict = {}

    LOG.info('key_list: %s', key_value_list.split(','))
    LOG.info('output_yaml: %s', output_yaml)

    yaml_dict = utils.update_yaml_dict_with_key_value_list(yaml_dict, key_value_list)

    with open(output_yaml, 'w', encoding="utf-8") as yaml_file:
        yaml.safe_dump(yaml_dict, yaml_file, allow_unicode=True)
