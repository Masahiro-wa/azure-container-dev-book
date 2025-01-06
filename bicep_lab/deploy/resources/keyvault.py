from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.keyvault.secrets import SecretClient
from .base import Base
from deploy.utils import context, log
import random, string

class Keyvault(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._keyvault_client = KeyVaultManagementClient(self.credential, self.subscription_id)

    def find_keyvault_by_prefix(self, rg_name, env_name) -> str:
        prefix = context.get_keyvault_name_prefix(env_name)
        try:
            keyvaults = self._keyvault_client.vaults.list_by_resource_group(rg_name)
            for keyvault in keyvaults:
                if keyvault.name.startswith(prefix):
                    return keyvault.name
            return ''
        except HttpResponseError as e:
            log.error(f"An error occurred while checking the Key Vault: {e}")
            raise e
    
    @staticmethod
    def generate_password(length=16):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        return password

    def get_sql_password_from_keyvault(self, vault_name: str, secret_name: str) -> str:
        vault_url = context.get_vault_url(vault_name)
        client = SecretClient(vault_url=vault_url, credential=self.credential)
        try:
            secret = client.get_secret(secret_name)
            return secret.value
        except ResourceNotFoundError:
            log.info(f"Secret {secret_name} not found in Key Vault {vault_name}")
            return ''
        except HttpResponseError as e:
            log.error(f"An error occurred while retrieving the secret from Key Vault: {e}")
            raise e
