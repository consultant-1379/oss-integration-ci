"""Module for the manipulating optionality related files."""
import logging
from pathlib import Path
import glob
import yaml

from . import helmfile
from . import utils

LOG = logging.getLogger(__name__)


def generate_optionality_maximum(state_values_file, path_to_helmfile, chart_cache_directory):
    """
    Generate an optionality maximum file, based on the provided helmfile and site values file.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml
        chart_cache_directory: the path to where the downloaded packages should be cached to/from

    Output:
        Writes updated yaml to state_values_file after enabling specified tags
    """
    LOG.info("Starting generating the optionality maximum file.")
    optionality_dicts = get_optionality_dicts(path_to_helmfile=path_to_helmfile, state_values_file=state_values_file,
                                              chart_cache_directory=chart_cache_directory)
    merged_optionality_dicts = logical_or_merge_optionality_dicts(optionality_dicts=optionality_dicts)
    __write_dict_to_yaml_file(yaml_file_path=Path(path_to_helmfile).parent /
                              'build-environment/optionality_maximum.yaml',
                              yaml_dict=merged_optionality_dicts)
    LOG.info("Finished generating the optionality maximum file.")


def get_optionality_dicts(path_to_helmfile, state_values_file, chart_cache_directory):
    """
    Return a list of optionality yaml dictionaries found in the helmfile and its dependencies.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml
        chart_cache_directory: the path to where the downloaded packages should be cached to/from

    Output:
        Returns a list of optionality dictionaries from the downloaded dependencies
    """
    optionality_dicts = [get_helmfile_optionality(path_to_helmfile=path_to_helmfile)]
    downloaded_charts_directory = helmfile.download_dependencies(path_to_helmfile=path_to_helmfile,
                                                                 state_values_file=state_values_file,
                                                                 chart_cache_directory=chart_cache_directory)
    for helm_chart in glob.glob(str(downloaded_charts_directory / Path('*.tgz'))):
        LOG.debug("Attempting to extract the optionality.yaml from chart %s", helm_chart)
        try:
            extracted_optionality_yaml = utils.extract_files_from_archive(
                archive_file_path=helm_chart, file_to_extract_path='optionality.yaml')[0]
        except FileNotFoundError:
            extracted_optionality_yaml = None

        if extracted_optionality_yaml:
            LOG.debug("Loading the optionality.yaml found from %s", helm_chart)
            with open(str(extracted_optionality_yaml), "r", encoding='utf-8') as yaml_file:
                optionality_dicts.append(yaml.safe_load(yaml_file))
    return optionality_dicts


def __write_dict_to_yaml_file(yaml_file_path, yaml_dict):
    """
    Write a dict to a yaml file.

    Input:
        yaml_file_path: The file to write to.
        yaml_dict: The yaml object to write into the file.

    Output:
        Writes the given dictionary to a yaml file
    """
    LOG.info("Creating %s", yaml_file_path)
    with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(yaml_dict, yaml_file)
    with open(yaml_file_path, encoding='utf-8') as yaml_file:
        LOG.debug(yaml_file.read())


def logical_or_merge_optionality_dicts(optionality_dicts):
    """
    Merge the optionality dicts doing a logical or on the enabled key values.

    Input:
        optionality_dicts: A list of optionality dictionaries to merge.

    Output:
        Returns a resulting optionality dictionary.
    """
    merged_optionality_dict = {}
    for optionality_dict in optionality_dicts:
        logical_or_extend_dict(extend_me=merged_optionality_dict, extend_by=optionality_dict)
    return merged_optionality_dict


def logical_or_extend_dict(extend_me, extend_by):
    """
    Merge the contents of a dictionary into an existing dictionary, recursively.

    Input:
        extend_me: Object to be extended.
        extend_by: Object to extend.

    Output:
        Updates the given extend_me object
    """
    if isinstance(extend_me, dict):
        for key, value in extend_by.items():
            if key in extend_me:
                if value is True:
                    extend_me[key] = value
                else:
                    logical_or_extend_dict(extend_me=extend_me[key], extend_by=value)
            else:
                extend_me[key] = value
    else:
        extend_me += extend_by


def get_helmfile_optionality(path_to_helmfile):
    """
    Get the optionality.yaml file contents as a dict if present.

    Input:
        path_to_helmfile: Path to the helmfile.yaml

    Output:
        Returns an optionality dictionary read from the base of the given helmfile.
    """
    try:
        with open(Path(path_to_helmfile).parent / 'optionality.yaml', encoding='utf-8') as optionality_yaml_file:
            return yaml.safe_load(optionality_yaml_file)
    except FileNotFoundError:
        return {}
