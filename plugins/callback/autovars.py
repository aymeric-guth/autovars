# -*- coding: utf-8 -*-
# Copyright (c) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

# v=playbook.get_plays()[0]
# r=v.get_roles()[0]


__metaclass__ = type

DOCUMENTATION = """
    author: Unknown (!UNKNOWN)
    name: log_plays
    type: notification
    short_description: write playbook output to log file
    description:
      - This callback writes playbook output to a file per host in the C(/var/log/ansible/hosts) directory
    requirements:
     - Whitelist in configuration
     - A writeable /var/log/ansible/hosts directory by the user executing Ansible on the controller
    options:
      log_folder:
        default: /var/log/ansible/hosts
        description: The folder where log files will be created.
        env:
          - name: ANSIBLE_LOG_FOLDER
        ini:
          - section: callback_log_plays
            key: log_folder
"""

import os
import time
import json

from ansible.utils.path import makedirs_safe
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.log_plays"
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(playbook)s - %(task_name)s - %(task_action)s - %(category)s - %(data)s\n\n"

    def __init__(self):

        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        print("set_options")
        super(CallbackModule, self).set_options(
            task_keys=task_keys, var_options=var_options, direct=direct
        )
        # print(dir(self))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        print("v2_runner_on_failed")

    def v2_runner_on_ok(self, result):
        print("v2_runner_on_ok called")

    def v2_playbook_on_start(self, playbook):
        print("v2_playbook_on_start")
        v = playbook.get_plays()[0]
        v.roles[0].vars.update({"test101": "123"})
        v.roles[0].vars.update({"var1": "alkdldqhi1hf1910pipn"})
        v.roles[0].vars.update({"_placeholder": "19r130y8vewiwe"})
        for i in v.roles[0].vars.keys():
            print(i)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        print("v2_playbook_on_import_for_host called")
