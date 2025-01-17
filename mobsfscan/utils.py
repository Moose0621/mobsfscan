# -*- coding: utf_8 -*-
"""Logger Config."""
from pathlib import Path

import mobsfscan.settings as config
from mobsfscan.logger import init_logger

import yaml


logger = init_logger(__name__)


def get_config(base_path, config_file):
    options = {
        'scan_extensions': config.SCAN_EXTENSIONS,
        'ignore_filenames': config.IGNORE_FILENAMES,
        'ignore_extensions': config.IGNORE_EXTENSIONS,
        'ignore_paths': config.IGNORE_PATHS,
        'ignore_rules': set(),
        'suppress_findings': {},
    }
    if config_file:
        cfile = Path(config_file)
    else:
        cfile = Path(base_path[0]) / config.MOBSFSCAN_CONFIG_FILE
    if cfile.is_file() and cfile.exists():
        extras = read_yaml(cfile)
        root = validate_config(extras, options)
        if not root:
            logger.warning('Invalid YAML, ignoring config from .mobsf')
            return options
        usr_scan_ext = root.get('scan-extensions')
        usr_ignore_files = root.get('ignore-filenames')
        usr_igonre_paths = root.get('ignore-paths')
        usr_ignore_exts = root.get('ignore-extensions')
        usr_ignore_rules = root.get('ignore-rules')
        use_suppress_finds = root.get('suppress-findings')
        if usr_scan_ext:
            options['scan_extensions'].update(usr_scan_ext)
        if usr_ignore_files:
            options['ignore_filenames'].update(usr_ignore_files)
        if usr_igonre_paths:
            options['ignore_paths'].update(usr_igonre_paths)
        if usr_ignore_exts:
            options['ignore_extensions'].update(usr_ignore_exts)
        if usr_ignore_rules:
            options['ignore_rules'].update(usr_ignore_rules)
        if use_suppress_finds:
            options['suppress_findings'].update(use_suppress_finds)
    return options


def validate_config(extras, options):
    """Validate user supplied config file."""
    if not extras:
        return False
    if isinstance(extras, dict):
        root = extras
    else:
        root = extras[0]
    valid = True
    for key, value in root.items():
        if key.replace('-', '_') not in options.keys():
            valid = False
            logger.warning('The config `%s` is not supported.', key)
        if key == 'suppress-findings' and not isinstance(value, dict):
            valid = False
            logger.warning('The value `%s` for the config `%s` is invalid.'
                           ' Only dict of value(s) are supported.', value, key)
        elif key != 'suppress-findings' and not isinstance(value, list):
            valid = False
            logger.warning('The value `%s` for the config `%s` is invalid.'
                           ' Only list of value(s) are supported.', value, key)
    if not valid:
        return False
    return root


def read_yaml(file_obj, text=False):
    """Read Yaml."""
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError:
        logger.error('Failed to parse YAML')
    except Exception:
        logger.exception('Error parsing YAML')
    return None
