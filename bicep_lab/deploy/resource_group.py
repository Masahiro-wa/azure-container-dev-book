from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from utils.log import log

def check_resource_group_exists(credential, subscription_id, resource_group_name):
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        return resource_client.resource_groups.check_existence(resource_group_name)
    except ResourceNotFoundError:
        return False
    except HttpResponseError as e:
        log.error(f"An error occurred while checking the resource group: {e}")
        raise Exception(f"An error occurred while checking the resource group: {e}")

def create_resource_group(credential, subscription_id, resource_group_name, location):
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        if check_resource_group_exists(credential, subscription_id, resource_group_name):
            return True
        return resource_client.resource_groups.create_or_update(resource_group_name, {'location': location})
    except HttpResponseError as e:
        log.error(f"An error occurred while creating the resource group: {e}")
        raise Exception(f"An error occurred while creating the resource group: {e}")
    
def delete_resource_group(credential, subscription_id, resource_group_name):
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        delete_async_operation = resource_client.resource_groups.begin_delete(resource_group_name)
        delete_async_operation.wait()
        return True
    except ResourceNotFoundError:
        log.error(f"Resource group {resource_group_name} not found.")
        raise Exception(f"Resource group {resource_group_name} not found.")
    except HttpResponseError as e:
        log.info(f"An error occurred while deleting the resource group: {e}")
        raise Exception(f"An error occurred while deleting the resource group: {e}")
