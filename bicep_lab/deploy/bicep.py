from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from deploy import vnet, acr, keyvault, role, dev_vm, db, app_container, front, back, scheduler
from utils.log import log
from utils import context
import json



def deploy_bicep_template(components: str, conf: dict, template_file: str):
    subscription_id = conf['subscription_id']
    resource_group_name = conf['resource_group_name']
    env_name = conf['env_name']
    credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)

    with open(template_file, 'r') as f:
        template = f.read()
    
    params = __get_params(components, conf)
    deployment_properties = {
        'mode': DeploymentMode.INCREMENTAL,
        'template': json.loads(template),
        'parameters': {k: {'value': v} for k, v in params.items()}
    }

    deployment_async_operation = resource_client.deployments.begin_create_or_update(
        resource_group_name,
        f'{env_name}-deployment',
        deployment_properties
    )
    deployment_async_operation.wait()
    

    print(f"Deployment of {components} completed.")

def __get_params(components: str, conf: dict, credential):
    params = {}
    for component in components:

        if component == 'role':
            return __role_params(conf)
        elif component == 'vnet':
            return __vnet_params(conf, credential)
        elif component == 'acr':
            return __acr_params(conf, credential) 
        elif component == 'keyvault':
            return __keyvault_params(conf, credential)
        elif component == 'dev_vm':
            return __dev_vm_params(conf)
        elif component == 'db':
            params.update(__db_params(conf['env_name'], conf['subscription_id'], conf['resource_group_name'], conf['template_file_path']))
        elif component == 'app_container':
            params.update(__app_container_params(conf['env_name'], conf['subscription_id'], conf['resource_group_name'], conf['template_file_path']))
        elif component == 'front':
            params.update(__front_params(conf['env_name'], conf['subscription_id'], conf['resource_group_name'], conf['template_file_path']))
        elif component == 'back':
            params.update(__back_params(conf['env_name'], conf['subscription_id'], conf['resource_group_name'], conf['template_file_path']))
        elif component == 'scheduler':
            params.update(__scheduler_params(conf['env_name'], conf['subscription_id'], conf['resource_group_name'], conf['template_file_path']))
        else:
            raise ValueError(f"Invalid component: {component}")
    return params  

def __role_params(conf: dict):
    params = {}
    params['vm_id_name'] = context.get_vm_id_name(conf['env_name'])
    params['backend_id_name'] = context.get_backend_id_name(conf['env_name'])
    params['frontend_id_name'] = context.get_frontend_id_name(conf['env_name'])
    params['scheduler_id_name'] = context.get_scheduler_id_name(conf['env_name'])

    return params

def __vnet_params(conf: dict, credential):
    params = {}
    if not vnet.check_cidr_available(credential, conf['subscription_id'], conf['vnet_cidr']):
        raise ValueError(f"VNet does not exist, but VNet CIDR {conf['vnet_cidr']} is already in use.")
    params['vnet_name'] = context.get_vnet_name(conf['env_name'])
    params['vnet_cidr'] = conf['vnet_cidr']
    params['dev_subnet_name'] = context.get_dev_subnet_name(conf['env_name'])
    params['dev_subnet_cidr'] = conf['dev_subnet_cidr']
    
    return params

def __acr_params(conf: dict, credential):
    params = {}
    acr_name = acr.find_acr_by_prefix(credential, conf['subscription_id'], conf['resource_group_name'], conf['env_name'])
    if acr_name:
        params['acr_name'] = acr_name
    else:
        params['acr_name'] = context.get_acr_name(conf['env_name'])
    params['vm_id_name'] = context.get_vm_id_name(conf['env_name'])
    
    return params

def __keyvault_params(conf: dict, credential):
    params = {}
    keyvault_name = keyvault.find_keyvault_by_prefix(credential, conf['subscription_id'], conf['resource_group_name'], conf['env_name'])
    if keyvault_name:
        params['keyvault_name'] = keyvault_name
    else:
        params['keyvault_name'] = context.get_unique_keyvault_name(conf['env_name'])
    params['sql_pass'] = keyvault.generate_password()
    
    return params

def __dev_vm_params(conf: dict):
    params = {}
    params['dev_vm_name'] = context.get_dev_vm_name(conf['env_name'])
    params['dev_vmss_name'] = context.get_dev_vmss_name(conf['env_name'])
    params['vm_id_name'] = context.get_vm_id_name(conf['env_name'])
    params['admin_username'] = conf['AdminUsername']
    params['admin_password'] = conf['AdminPassword']
    params['use_ssh'] = True if conf['UseSsh'].lower() == 'true' else False
    params['vm_size'] = conf['DevVmSize']
    params['ubuntu_os_version'] = conf['UbuntuOsVersion']
    params['vnet_name'] = context.get_vnet_name(conf['env_name'])
    params['subnet_name'] = context.get_dev_subnet_name(conf['env_name'])
    params['os_disk_type'] = conf['OsDiskType']
    
    return params
