# Copyright 2017 RedHat, inc
# (c) 2020, Technische Universität Dresden, School of Science, Robin Richter <robin.richter@mailbox.tu-dresden.de>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
vars: sdm_host_group_vars
license: GLP-3 license
version_added: "2.9"
short_description: In charge of loading group_vars and host_vars
description:
    - Loads YAML vars into corresponding groups/hosts in group_vars/ and host_vars/ directories.
    - Files are restricted by extension to one of .yaml, .json, .yml or no extension.
    - Hidden (starting with '.') and backup (ending with '~') files and directories are ignored.
    - Only applies to inventory sources that are existing paths.
    - Starting in 2.10, this plugin requires whitelisting and is whitelisted by default.
options:
  stage:
    ini:
      - key: stage
        section: vars_sdm_host_group_vars
    env:
      - name: ANSIBLE_VARS_PLUGIN_STAGE
  _valid_extensions:
    default: [".yml", ".yaml", ".json"]
    description:
      - "Check all of these extensions when looking for 'variable' files which should be YAML or JSON or vaulted versions of these."
      - 'This affects vars_files, include_vars, inventory and vars plugins among others.'
    env:
      - name: ANSIBLE_YAML_FILENAME_EXT
    ini:
      - section: yaml_valid_extensions
        key: defaults
    type: list
authors:
  - Robin Richter <robin.richter@mailbox.tu-dresden.de>

extends_documentation_fragment:
  - vars_plugin_staging
"""

import os
import pdb
from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.utils.vars import merge_hash

FOUND = {}


class VarsModule(BaseVarsPlugin):
    def get_vars(self, loader, path, entities, cache=True):
        """parses the inventory file"""

        pdb.set_trace()
        if not isinstance(entities, list):
            entities = [entities]

        super(VarsModule, self).get_vars(loader, path, entities)

        data = {}

        for entity in entities:
            if isinstance(entity, Host):
                subdir = "host_vars"
                data = self.get_vars(loader, path, entity.get_groups()[::-1])
            elif isinstance(entity, Group):
                subdir = "group_vars"

                if entity.name == "all":
                    data.update({"sdm_rootdir": os.getcwd()})
                    data.update(
                        {"sdm_keystore": "{}/keystore".format(data["sdm_rootdir"])}
                    )
                    data.update(
                        {"sdm_passwords": "{}/passwords".format(data["sdm_keystore"])}
                    )
                    data.update(
                        {"sdm_passwordrules": "chars=ascii_letters,digits length=15"}
                    )
                    data.update(
                        {"sdm_sshkeys": "{}/sshkeys".format(data["sdm_keystore"])}
                    )
                    data.update(
                        {
                            "sdm_certificates": "{}/certificates".format(
                                data["sdm_keystore"]
                            )
                        }
                    )
                    data.update(
                        {"sdm_customfiles": "{}/files".format(data["sdm_rootdir"])}
                    )
                    data.update(
                        {
                            "sdm_customtemplates": "{}/templates".format(
                                data["sdm_rootdir"]
                            )
                        }
                    )
            else:
                raise AnsibleParserError(
                    "Supplied entity must be Host or Group, got {} instead".format(
                        type(entity)
                    )
                )

            # avoid 'chroot' type inventory hostnames /path/to/chroot
            if not entity.name.startswith(os.path.sep):
                try:
                    found_files = []
                    # load vars
                    b_opath = os.path.realpath(
                        to_bytes(os.path.join(self._basedir, subdir))
                    )
                    opath = to_text(b_opath)
                    key = "{}.{}".format(entity.name, opath)
                    if cache and key in FOUND:
                        found_files = FOUND[key]
                    else:
                        # no need to do much if path does not exist for basedir
                        if os.path.exists(b_opath):
                            if os.path.isdir(b_opath):
                                self._display.debug("\tprocessing dir {}".format(opath))
                                found_files = loader.find_vars_files(opath, entity.name)
                                FOUND[key] = found_files
                            else:
                                self._display.warning(
                                    "Found {} that is not a directory, skipping: {}".format(
                                        subdir, opath
                                    )
                                )

                    for found in found_files:
                        new_data = loader.load_from_file(found, cache=True, unsafe=True)
                        if new_data:  # ignore empty files
                            try:  # ansible version 2.10 and newer
                                data = merge_hash(
                                    data, new_data, recursive=True, list_merge="append"
                                )
                            except TypeError:  # ansible version 2.9 and older
                                data = merge_hash(data, new_data)

                except Exception as e:
                    raise AnsibleParserError(to_native(e))

        return data
