from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.identity import DefaultAzureCredential

def check_vnet_exists(credential, subscription_id, resource_group_name, vnet_name):
    network_client = NetworkManagementClient(credential, subscription_id)
    try:
        vnet = network_client.virtual_networks.get(resource_group_name, vnet_name)
        if vnet:
            return True
        return False
    except ResourceNotFoundError:
        return False
    except HttpResponseError as e:
        print(f"An error occurred while checking the VNet: {e}")
        raise

def check_cidr_available(credential, subscription_id, cidr):
    if check_vnet_exists(credential, subscription_id, cidr):
        return True
    network_client = NetworkManagementClient(credential, subscription_id)
    try:
        vnets = network_client.virtual_networks.list_all()
        for vnet in vnets:
            for address_space in vnet.address_space.address_prefixes:
                if cidr == address_space:
                    return False
        return True
    except HttpResponseError as e:
        print(f"An error occurred while checking the CIDR: {e}")
        raise
