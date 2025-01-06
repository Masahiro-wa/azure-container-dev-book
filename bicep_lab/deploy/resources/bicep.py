from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from deploy.utils import context, log
from .base import Base
import json
import os
import subprocess

class Bicep(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    def deploy(self, deploy_name: str, template_file_path: str, rg_name: str, 
                              params_file_path : str, mode: str = 'incremental') -> bool:
        """
        Function to deploy a Bicep template

        Args:
            deploy_name (str): Name of the bicep deployment
            template_file_path (str): Path to the template file
            rg_name (str): Name of the resource group
            params_file_path  (str): Parameter information
            mode (str): Deployment mode (only 'incremental' or 'complete' can be specified)

        """
        try:
            with open(template_file_path, 'r') as f:
                template = f.read()
        except FileNotFoundError as e:
            log.error(f"Template file not found: {e}")
            raise
        try:
            self.deploy_bicep_with_params(template_file_path, rg_name, params_file_path)
        except Exception as e:
            log.error(f"Error during deployment: {deploy_name}")
            log.error(e)
            raise e
        return True

    @staticmethod
    def deploy_bicep_with_params(template_file, resource_group, params_file_path):
        try:
            cmd = [
                "az", "deployment", "group", "create",
                "--resource-group", resource_group,
                "--template-file", template_file,
                "--parameters", params_file_path
            ]
            
            # コマンド実行
            subprocess.run(cmd, check=True)
        finally:
            # 一時ファイルを削除
            os.remove(params_file_path)
