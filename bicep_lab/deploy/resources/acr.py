from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.core.exceptions import  HttpResponseError
from .base import Base
from deploy.utils import context, log

class Acr(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._acr_client = ContainerRegistryManagementClient(self.credential, self.subscription_id)

    def find_acr_by_prefix(self, resource_group_name, env_name) -> str:
        prefix = context.get_acr_name_prefix(env_name)
        try:
            registries = self._acr_client.registries.list_by_resource_group(resource_group_name)
            for registry in registries:
                if registry.name.startswith(prefix):
                    return registry.name
            return ''
        except HttpResponseError as e:
            log.error(f"An error occurred while checking the ACR: {e}")
            raise
