from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from deploy.utils import log
from .base import Base

class ResourceGroup(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    def check_resource_group_exists(self, rg_name):
        try:
            return self._resource_client.resource_groups.check_existence(rg_name)
        except HttpResponseError as e:
            log.error(f"An error occurred while checking the resource group: {e}")
            raise e
        except Exception as e:
            log.error(f"An error occurred while checking the resource group: {e}")
            raise e

    def create_resource_group(self, rg_name, location):
        try:
            self._resource_client.resource_groups.create_or_update(rg_name, {'location': location})
            return True
        except HttpResponseError as e:
            log.error(f"An error occurred while creating the resource group: {e}")
            raise e
        except Exception as e:
            log.error(f"An error occurred while creating the resource group: {e}")
            raise e
        
    def delete_resource_group(self, rg_name: str):
        try:
            delete_async_operation = self._resource_client.resource_groups.begin_delete(rg_name)
            delete_async_operation.wait()
            return True
        except ResourceNotFoundError:
            log.info(f"Resource group {rg_name} not found.")
        except HttpResponseError as e:
            log.info(f"An error occurred while deleting the resource group: {e}")
            raise e
