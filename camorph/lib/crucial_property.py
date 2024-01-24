import json
import re
import warnings
import os
from os.path import isdir, dirname, isfile, basename

import numpy as np

from model import Camera
from model.FileHandler import FileHandler

"""
This module is used to check if the crucial properties of a destination FileHandler have been set
when trying to write to a file. For example, all photogrammetry formats (COLMAP, RealityCapture, Mehsroom) need
source_image property. This can be set by supplying a config.json file. Camorph automatically looks for
a config.json file in the target directory.
"""


def cmd_check_properties(inst: FileHandler, cams: list[Camera]) -> None:
    pass


def pip_check_properties(inst: FileHandler, cams: list[Camera], crucial_property_config: str, dest_path: str) -> None:
    # This function checks if crucial properties are set, and sets them via a config
    crucial_properties = inst.crucial_properties()
    crucial_property_config = os.path.join(dest_path, 'config.json') if isdir(dest_path) else os.path.join(dirname(dest_path), 'config.json')

    cpc = None
    if isfile(crucial_property_config):
        print('Found config.json')
        with open(crucial_property_config, 'r') as f:
            cpc = json.load(f)

        # set all attributes in config.json
        if 'values' in cpc:
            for val in cpc['values']:
                for prop in val:
                    try:
                        set_config_property(next(cam for cam in cams if cam.name == val['name']), prop, val[prop])
                    except StopIteration:
                        raise Exception("At least one camera supplied in the config file was not found in the source file. Are you using a wrong config.json ?")

        for prop in cpc['global']:
            if prop[prop.rfind('_'):] == '_path':
                prop = prop[:prop.rfind('_')]
                p = cpc['global'][prop + '_path']['path']
                if 'filter' in cpc['global'][prop + '_path']:
                    regex = cpc['global'][prop + '_path']['filter']
                else:
                    regex = '.*'
                files = [os.path.relpath(os.path.join(p,f),os.path.dirname(dest_path)) for f in os.listdir(p) if bool(re.match(regex, basename(f)))]
                # os.listdir() returns random order when path is a network path
                files = sorted(files)
                
                unmatched_files = []
                for file in files:
                    # match files according to camera names
                    filename = basename(file)
                    try:
                        found_cam = next(
                            (cam for cam in cams if (cam.name[:cam.name.rfind('.')] == filename[:filename.rfind('.')] if '.' in cam.name else cam.name == filename[:filename.rfind('.')])),
                            None)
                    except TypeError:
                        # cam.name is None and cant be iterated
                        found_cam = None
                    if found_cam is not None and hasattr(found_cam,prop) and getattr(found_cam,prop) is None:
                        set_config_property(found_cam, prop, file)
                    else:
                        unmatched_files.append(file)
                if len(unmatched_files) > 0:
                    warnings.warn("Not all files match Camera names, resorting to order of files in os")
                    idx = 0
                    for cam in cams:
                        if getattr(cam,prop) is None:
                            try:
                                set_config_property(cam, prop, unmatched_files[idx])
                                idx += 1
                            except IndexError:
                                raise Exception(f"There are less files than cameras found:"
                                                f" {len(files)} files, {len(cams)} cameras")
            else:
                for cam in cams:
                    if isinstance(cpc['global'][prop], list):
                        set_config_property(cam, prop, np.asarray(cpc['global'][prop]))
                    else:
                        set_config_property(cam, prop, cpc['global'][prop])

    # check if any cam doesn't have this attribute or if it is None
    unset_properties = []
    unset_json_properties = dict()
    for prop in crucial_properties:
        for cam in cams:
            if not hasattr(cam, prop) or getattr(cam, prop) is None:
                if cpc is not None:
                    if prop not in unset_json_properties:
                        unset_json_properties[prop] = []
                    unset_json_properties[prop].append(cam.name)
                else:
                    if prop not in unset_properties:
                        unset_properties.append(prop)

    # check if json was supplied, but not all properties were set
    if len(unset_json_properties) > 0:
        errstring = "Not all crucial properties have been set in config.json. The following properties are missing: \n"
        for key in unset_json_properties:
            errstring += key + ' on cameras ' + ','.join([str(x) for x in unset_json_properties[key]]) + '\n'
        errstring += 'Camorph can automatically compute some parameters. Please refer to the documentation.'
        raise Exception(errstring)

    # check if unset properties exist
    if len(unset_properties) > 0:
        if not isfile(crucial_property_config):
            write_crucial_config_template(cams, crucial_property_config, unset_properties)
            raise Exception("Crucial properties are missing and no config.json file was found in the output folder. A "
                            "config.json template has been generated. The following curcial properties are missing: " +
                            ' '.join([str(x) for x in unset_properties]))
        else:
            raise Exception(
                "This error should not occur. There are no unset json properties but a config.json exists. Please "
                "contact support")


def set_config_property(cam, property, value):
    # name property cannot be set as it is used as a unique identifier for cameras
    if property == 'name':
        return
    if hasattr(cam, property) and getattr(cam, property) is not None:
        warnings.warn('Config.json is overriding existing property ' + property + ' of value ' + str(getattr(cam, property)) + ' with value ' + str(value))
    setattr(cam, property, value)

def write_crucial_config_template(cams, path, properties=None):
    """
    This function writes a config.json template file to the specified location.
    When trying to write to a format with missing crucial properties, camorph automatically
    writes a config.json file to the target path.
    
    :param cams: A list of cameras
    :param path: The path where to write the config.json file
    :param properties: Optional missing properties
    :return:
    """
    if properties is None:
        properties = []
    template = dict()
    template['type'] = "camorph_config"
    template['missing_properties'] = []
    for prop in properties:
        template['missing_properties'].append(prop)
    template['example'] = {"property_name": "Value", "global_path": {"path": r"\path\to\dir", "filter": "regex"}}
    template['global'] = {}
    template['values'] = []
    for c in cams:
        template['values'].append({'name': c.name})
    with open(path, 'w') as f:
        json.dump(template, f, indent=4)
