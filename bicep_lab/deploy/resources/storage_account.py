from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient
from base import Base
from utils import context, log
import os

class StorageAccount(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._storage_client = StorageManagementClient(self.credential, self.subscription_id)

    def find_storage_account_by_prefix(self, resource_group_name, env_name) -> str:
        prefix = context.get_storage_account_name_prefix(env_name)
        try:
            accounts = self._storage_client.storage_accounts.list_by_resource_group(resource_group_name)
            for account in accounts:
                if account.name.startswith(prefix):
                    return account.name
            return ''
        except HttpResponseError as e:
            log.error(f"An error occurred while checking the storage accounts: {e}")
            raise
    
    def upload_file_to_container(self, account_name, container_name, file_path) -> bool:
        try:
            account_url = context.get_storage_account_url(account_name)
            blob_service_client = BlobServiceClient(account_url=account_url, credential=self.credential)
            blob_name = os.path.basename(file_path)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data)
            return True
        except Exception as e:
            log.error(f"An error occurred while uploading the file to the container: {e}")
            raise e
