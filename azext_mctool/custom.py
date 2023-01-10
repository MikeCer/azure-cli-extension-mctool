# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
import typer
from rich.console import Console
from rich.table import Table

from azure.cli.core.profiles import ResourceType, supported_api_version
from azure.cli.command_modules.network._client_factory import network_client_factory

import ipaddress

console = Console()

def calculate_free_subnets(address_space, used_subnets, min_size):
  network = ipaddress.ip_network(address_space)

  if min_size < network.prefixlen:
    return list()

  preflen_subnets_diff = min_size - network.prefixlen

  used_subnets = [ipaddress.ip_network(subnet) for subnet in used_subnets]

  free_subnets = []

  for subnet in network.subnets(preflen_subnets_diff):
    overlap_excluded = False
    for used_subnet in used_subnets:
        if subnet.overlaps(used_subnet):
            overlap_excluded = True
            break

    if overlap_excluded == False:
        free_subnets.append(subnet)

  return free_subnets

def vnet_search_free_subnets(cmd, resource_group_name, vnet_name, search_network_size, plain_output=False):     

    ncf = network_client_factory(cmd.cli_ctx)
    vnet = ncf.virtual_networks.get(resource_group_name, vnet_name) 

    table_vnet = Table(vnet.name)
    
    table_addr_space = Table()
    table_addr_space.add_column("Address Space", style="Blue", vertical="middle")
    table_addr_space.add_column("Subnets")

    for addrs_prefs in vnet.address_space.address_prefixes:
        vnet_addrs = ipaddress.ip_network(addrs_prefs)
        used_subnets = []

        table_subnets = Table()
        table_subnets.add_column("CIDR")
        table_subnets.add_column("IP Min")
        table_subnets.add_column("IP Max")
        table_subnets.add_column("Netmask")
        table_subnets.add_column("Num IPs")
        table_subnets.add_column("Name")
    
        for subnet in vnet.subnets:
            subnet_addr = ipaddress.ip_network(subnet.address_prefix)
            if subnet_addr.subnet_of(vnet_addrs):
                
                table_subnets.add_row(str(subnet_addr),str(subnet_addr[0]), str(subnet_addr[-1]), str(subnet_addr.netmask), str(subnet_addr.num_addresses), subnet.name, style="Yellow")

                used_subnets.append(ipaddress.IPv4Network(subnet.address_prefix))

        free_subnet = calculate_free_subnets(addrs_prefs, used_subnets, int(search_network_size))        

        for fs in free_subnet:
            table_subnets.add_row(str(fs),str(fs[0]), str(fs[-1]), str(fs.netmask), str(fs.num_addresses), "FREE", style="Green")

            if (plain_output == True):
                print(fs)

        table_addr_space.add_row(addrs_prefs, table_subnets)
        
    table_vnet.add_row(table_addr_space)
    
    if (plain_output == False):
        console.print(table_vnet)        

def update_mctool(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance