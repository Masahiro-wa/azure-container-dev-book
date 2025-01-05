from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from utils import context, log
from base import Base
import json

class Bicep(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    def deploy(self, deploy_name: str, template_file_path: str, rg_name: str, 
                              params: dict, mode: str = 'incremental') -> bool:
        """
        Function to deploy a Bicep template

        Args:
            deploy_name (str): Name of the bicep deployment
            template_file_path (str): Path to the template file
            rg_name (str): Name of the resource group
            params (dict): Parameter information
            mode (str): Deployment mode (only 'incremental' or 'complete' can be specified)

        """
        deploy_mode = DeploymentMode.INCREMENTAL
        if mode == 'complete':
            deploy_mode = DeploymentMode.COMPLETE
        template = None
        try:
            with open(template_file_path, 'r') as f:
                template = f.read()
        except FileNotFoundError as e:
            log.error(f"Template file not found: {e}")
            raise
        deployment_properties = {
            'mode': deploy_mode,
            'template': json.loads(template),
            'parameters': {k: {'value': v} for k, v in params.items()}
        }
        try:
            deployment_async_operation = self._resource_client.deployments.begin_create_or_update(
                resource_group_name=rg_name,
                deployment_name=deploy_name,
                parameters=deployment_properties
            )
            deployment_async_operation.wait()
        except Exception as e:
            log.error(f"Error during deployment: {e}")
            raise e
        return True
