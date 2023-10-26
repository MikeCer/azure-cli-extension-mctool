# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.profiles import ResourceType, supported_api_version
from ._client_factory import network_client_factory
from knack.log import get_logger
from knack.util import CLIError
import ipaddress
import os
import sys
import typer
from rich.console import Console
from rich.table import Table

logger = get_logger(__name__)

def _ensure_deps():
    try:
        import typer
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        import subprocess
        logger.warning("Installing dependencies required ...")
        from azure.cli.core.extension import EXTENSIONS_DIR
        mctool_ext_path = os.path.join(EXTENSIONS_DIR, 'mctool')
        python_path = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = python_path + ':' + mctool_ext_path if python_path else mctool_ext_path
        cmd = [sys.executable, '-m', 'pip', 'install', '--target', mctool_ext_path,
               'rich ', '-vv', '--disable-pip-version-check', '--no-cache-dir']
        logger.warning('Installing "typer" and "rich" pip packages')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        logger.warning(result.stdout.decode('utf-8'))
        logger.warning('Installation completed')
        
        #subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        
        

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
    
    #_ensure_deps()

    console = Console()


    #ncf = network_client_factory(cmd.cli_ctx)
    #vnet = ncf.virtual_networks.get(resource_group_name, vnet_name) 

    from .aaz.latest.network.vnet import Show
    vnet = Show(cli_ctx=cmd.cli_ctx)(command_args={
        "name": vnet_name,
        "resource_group": resource_group_name,
    })

    table_vnet = Table(vnet["name"])
    
    table_addr_space = Table()
    table_addr_space.add_column("Address Space", style="Blue", vertical="middle")
    table_addr_space.add_column("Subnets")

    for addrs_prefs in vnet["addressSpace"]["addressPrefixes"]:
        vnet_addrs = ipaddress.ip_network(addrs_prefs)
        used_subnets = []

        table_subnets = Table()
        table_subnets.add_column("CIDR")
        table_subnets.add_column("IP Min")
        table_subnets.add_column("IP Max")
        table_subnets.add_column("Netmask")
        table_subnets.add_column("Num IPs")
        table_subnets.add_column("Name")
    
        for subnet in vnet["subnets"]:
            subnet_addr = ipaddress.ip_network(subnet["addressPrefix"])
            if subnet_addr.subnet_of(vnet_addrs):
                
                table_subnets.add_row(str(subnet_addr),str(subnet_addr[0]), str(subnet_addr[-1]), str(subnet_addr.netmask), str(subnet_addr.num_addresses), subnet["name"], style="Yellow")

                used_subnets.append(ipaddress.IPv4Network(subnet["addressPrefix"]))

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