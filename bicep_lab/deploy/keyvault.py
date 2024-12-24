from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.core.exceptions import HttpResponseError
from azure.keyvault.secrets import SecretClient
from utils import context
from utils.log import log
import random, string

def find_keyvault_by_prefix(credential, subscription_id, resource_group_name, env_name) -> str:
    keyvault_client = KeyVaultManagementClient(credential, subscription_id)
    prefix = context.get_keyvault_name_prefix(env_name)
    try:
        keyvaults = keyvault_client.vaults.list_by_resource_group(resource_group_name)
        for keyvault in keyvaults:
            if keyvault.name.startswith(prefix):
                return keyvault.name
        return None
    except HttpResponseError as e:
        log.error(f"An error occurred while checking the Key Vault: {e}")
        raise

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def get_sql_password_from_keyvault(credential, vault_name, secret_name):
    vault_url = f"https://{vault_name}.vault.azure.net/"
    client = SecretClient(vault_url=vault_url, credential=credential)
    try:
        secret = client.get_secret("sqlPass")
        return secret.value
    except HttpResponseError as e:
        log.error(f"An error occurred while retrieving the secret from Key Vault: {e}")
        raise


