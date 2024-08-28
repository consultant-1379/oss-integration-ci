"""Module to manage merging of yaml data."""
# pylint: disable=C0123
import logging
import oyaml as yaml  # pip install oyaml
from yaml import SafeDumper

LOG = logging.getLogger(__name__)
ERROR_IN_DEPLOYMENT = False

SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:null', '')
  )


# PRIVATE FUNCTIONS

def _merge_dict(base, override, values_only):
    """
    Update base dictionary yaml with override values, or warn if matching key not found in base.

    Input:
        base: Dictionary representing base yaml to compare with override yaml
        override: Dictionary representing override yaml to compare with base yaml
        values_only: "true" to log warning only if missing key in base compared with override

    Output:
        Updated base yaml
    """
    for k in override:
        if values_only == "true" and k not in base:
            LOG.warning("Skipping %s as key, %s not found in main site values section %s",
                        str(override[k]), str(k), str(base))
            continue
        if k == 'tags':
            base[k] = override[k]
        elif isinstance(override[k], (dict, list)) is False \
                or k not in base \
                or type(base[k]) != type(override[k]):  # noqa: E721
            base[k] = override[k]
        elif isinstance(override[k], list):
            base[k] = override[k]
        else:
            base[k] = _merge_dict(base[k], override[k], values_only)
    return base


# pylint: disable=assignment-from-no-return
def _check_dict(base, override, exit_deployment):
    """
    Log an error if base contains a key that is not present in override dictionary.

    Input:
        base: Dictionary representing base yaml to compare with override yaml

    Output:
        Log error if an entry in base is missing from override yaml
    """
    global ERROR_IN_DEPLOYMENT  # pylint: disable=global-statement
    ERROR_IN_DEPLOYMENT = exit_deployment
    for k in base:
        if k not in override:
            LOG.error("Error for %s as key, %s not found in CI site values section %s",
                      str(base[k]), str(k), str(override))
            ERROR_IN_DEPLOYMENT = True
            continue
        if k == 'tags':
            override[k] = base[k]
        elif isinstance(base[k], (dict, list)) is False \
                or k not in override \
                or type(override[k]) != type(base[k]):  # noqa: E721
            override[k] = base[k]
        elif isinstance(base[k], list):
            override[k] = base[k]
        else:
            override[k] = _check_dict(base[k], override[k], ERROR_IN_DEPLOYMENT)
    return ERROR_IN_DEPLOYMENT


# PUBLIC FUNCTIONS

def merge_data(base, override, values_only):
    """
    Return a dictionary or list with same content of 'base' overrided by the content of 'override'.

    Input:
        base: Base yaml structure to update
        override: Yaml to compare with base and potentially replace what is in base
        values_only: "true" will log a warning if override key is missing from base (but will not
                     update base yaml), and log an error if base contains a key that is not present
                     in override dictionary

    Output:
        Returns updated base yaml
    """
    # This function copies 'base' and update its contents: what is in 'override' that is not in 'base'
    # will be added and if the same key in 'override' has a different value in 'base' then
    # the value from 'override' will be taken
    if type(override) is not type(base):
        return None, "'base.yaml' and 'override.yaml' have different structure"
    if type(override) is list:
        return override, None
    merged_base = _merge_dict(dict(base), dict(override), values_only), None
    if values_only == "true":
        exit_deployment = _check_dict(dict(base), dict(override), ERROR_IN_DEPLOYMENT)
        if exit_deployment:
            raise Exception("""Exiting deployment due to missing variables in the CI site values
                             compared to the DM Prepared site values""")
    return merged_base


def merge_yaml(base_yaml, override_yaml, values_only):
    """Merge two files and return the resulting dictionary or list.

    Input:
        base_yaml: Base yaml file to load
        override_yaml: Override yaml file to load
        values_only: "true" log warning if missing keys in base (compared to override),
                     and log error if base contains keys that are missing from override

    Output:
        Updated base yaml with updates from override
    """
    LOG.info("Merging override yaml file %s with file %s", override_yaml, base_yaml)
    with open(base_yaml, "r", encoding="utf-8") as base_yaml_data:
        base = yaml.safe_load(base_yaml_data)
    with open(override_yaml, "r", encoding="utf-8") as override_yaml_data:
        override = yaml.safe_load(override_yaml_data)
    if override is None or override == '':
        return base, None
    return merge_data(base, override, values_only)


def merge_files_create_new_output_file(base_yaml, override_yaml, output_yaml, values_only="false"):
    """
    Update base yaml from file with overrides from file and generate a new merged yaml file.

    Input:
        base_yaml: Base yaml file to load
        override_yaml: Override yaml file to load
        output_yaml: Yaml file(s) to write with updated base yaml.  CSV format if more than
                     one file provided
        values_only: "true" if missing keys between base/override should be logged
    """
    LOG.info('Inputted parameters:')
    LOG.info('base_yaml: %s', base_yaml)
    LOG.info('override_yaml: %s', override_yaml)
    LOG.info('output_yaml: %s', output_yaml)
    LOG.info('values_only: %s', values_only)

    # Determine number of override yaml files to merge
    override_yaml_files = override_yaml.strip().split(",")
    for override_yaml_file in override_yaml_files:
        override_yaml_file = override_yaml_file.strip()
        data_merged, err = merge_yaml(base_yaml, override_yaml_file, values_only)
        if data_merged is None:
            err_msg = '[%s] Error: %s', base_yaml, err
            LOG.error(err_msg)
            raise Exception(err_msg)
        # If more than 1 override yaml is provided, keep re-using the same file
        # as the new base
        with open(output_yaml, 'w', encoding="utf-8") as output_yaml_file:
            yaml.safe_dump(data_merged, output_yaml_file, default_flow_style=False)
        # Set the new base to the merged data file, in case there's more than 1 override
        base_yaml = output_yaml
