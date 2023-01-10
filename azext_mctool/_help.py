# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['mctool'] = """
    type: group
    short-summary: Commands to manage Mctools.
"""

helps['mctool vnet'] = """
    type: group
    short-summary: Custom extension to manage vnet
"""

helps['mctool vnet list-free-subnets'] = """
    type: command
    short-summary: search for free subnets on the specified vnet
"""
