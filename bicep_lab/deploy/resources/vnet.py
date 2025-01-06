from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.network.models import VirtualNetwork
from .base import Base
from deploy.utils import log

class Vnet(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._network_client = NetworkManagementClient(self.credential, self.subscription_id)
    
    def get_vnet_by_name(self, rg_name: str, vnet_name: str) -> VirtualNetwork:
        try:
            return self._network_client.virtual_networks.get(rg_name, vnet_name)
        except ResourceNotFoundError:
            return None
        except HttpResponseError as e:
            log.error(f"An error occurred while checking the VNet: {e}")
            raise e
        except Exception as e:
            log.error(f"An error occurred while checking the VNet: {e}")
            raise e
    
    def check_vnet_cidr_availability(self, cidr: str) -> bool:
        try:
            vnets = self._network_client.virtual_networks.list_all()
            address_spaces = [address_space for vnet in vnets for address_space in vnet.address_space.address_prefixes]
            if cidr in address_spaces:
                return False
            return True
        except Exception as e:
            log.error(f"An error occurred while checking the CIDR availability: {e}")
            raise e
    
    def check_subnet_cidr_availability(self, vnet_name: str, rg_name: str, cidr: str) -> bool:
        try:
            subnets = self._network_client.subnets.list(rg_name, vnet_name)
            subnet_cidrs = [subnet.address_prefix for subnet in subnets]
            if cidr in subnet_cidrs:
                return False
            return True
        except Exception as e:
            log.error(f"An error occurred while checking the CIDR availability: {e}")
            raise e

    def delete_vnet(self, rg_name: str, vnet_name: str) -> bool:
        try:
            delete_async_operation = self._network_client.virtual_networks.begin_delete(rg_name, vnet_name)
            delete_async_operation.wait()
            return True
        except ResourceNotFoundError:
            log.info(f"VNet {vnet_name} not found.")
        except HttpResponseError as e:
            log.info(f"An error occurred while deleting the VNet: {e}")
            raise e
        except Exception as e:
            log.error(f"An error occurred while deleting the VNet: {e}")
            raise e
