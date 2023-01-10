# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from ._validators import get_search_network_size_validator

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    mctool_name_type = CLIArgumentType(options_list='--mctool-name-name', help='Name of the Mctool.', id_part='name')

    with self.argument_context('mctool') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('mctool_name', mctool_name_type, options_list=['--name', '-n'])

    with self.argument_context('mctool list') as c:
        c.argument('mctool_name', mctool_name_type, id_part=None)

    with self.argument_context('mctool vnet search-free-subnets') as c:
        c.argument('search_network_size', validator=get_search_network_size_validator(), help='Network size expressed as integer between 0 and 32')
        c.argument('plain_output', help='Get all the free subnets as plain text output')
        c.argument('vnet_name', help='Name of the vnet in which to search for free subnets')
