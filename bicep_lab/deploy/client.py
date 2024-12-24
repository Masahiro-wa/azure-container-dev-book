from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

class AzureClient:
    def __init__(self, subscription_id):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.blob_service_client = None

    def deploy_bicep_template(self, resource_group_name, template_file_path, parameters):
        with open(template_file_path, 'r') as template_file:
            template = template_file.read()

        deployment_properties = {
            'mode': DeploymentMode.INCREMENTAL,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.resource_client.deployments.begin_create_or_update(
            resource_group_name,
            'azure-sample',
            deployment_properties
        )
        deployment_async_operation.wait()
        print(f"Deployment of {template_file_path} completed.")

    def upload_file_to_blob(self, connection_string, container_name, file_path):
        if not self.blob_service_client:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=os.path.basename(file_path))

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        print(f"File {file_path} uploaded to container {container_name}.")

# 使用例
if __name__ == "__main__":
    subscription_id = 'your-subscription-id'
    resource_group_name = 'your-resource-group'
    template_file_path = 'path/to/your/template.bicep'
    parameters = {
        'param1': {'value': 'value1'},
        'param2': {'value': 'value2'}
    }
    connection_string = 'your-storage-account-connection-string'
    container_name = 'your-container-name'
    file_path = 'path/to/your/file.txt'

    client = AzureClient(subscription_id)
    client.deploy_bicep_template(resource_group_name, template_file_path, parameters)
    client.upload_file_to_blob(connection_string, container_name, file_path)