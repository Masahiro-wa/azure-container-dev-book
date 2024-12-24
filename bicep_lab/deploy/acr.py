from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.core.exceptions import  HttpResponseError
from utils import context
from utils.log import log

def find_acr_by_prefix(credential, subscription_id, resource_group_name, env_name) -> str:
    acr_client = ContainerRegistryManagementClient(credential, subscription_id)
    prefix = context.get_acr_name_prefix(env_name)
    try:
        registries = acr_client.registries.list_by_resource_group(resource_group_name)
        for registry in registries:
            if registry.name.startswith(prefix):
                return registry.name
        return ''
    except HttpResponseError as e:
        log.error(f"An error occurred while checking the ACR: {e}")
        raise
