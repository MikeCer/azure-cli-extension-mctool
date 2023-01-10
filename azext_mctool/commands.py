# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_mctool._client_factory import cf_mctool



def load_command_table(self, _):

    # TODO: Add command type here
    # mctool_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_mctool)

    with self.command_group('mctool', is_preview=True):
        pass

    with self.command_group('mctool vnet', is_preview=True) as g:
        g.custom_command('search-free-subnets','vnet_search_free_subnets')