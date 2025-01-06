import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from deploy.utils import log, context, files
from deploy.resources import Bicep, Vnet, Acr, Keyvault, SqlDb, StorageAccount
from deploy.common import core_deploy_files, apps_deploy_files, core_parallel_groups, apps_parallel_groups

def run_deployment(conf: dict, sorted_components: list):
    bicep_dir_path = os.path.join(conf['RootPath'], 'bicep')
    tmp_dir_path = os.path.join(conf['RootPath'], 'tmp')
    parallel_groups = core_parallel_groups + apps_parallel_groups
    bicep = Bicep(conf['subscription_id'])

    def deploy_component(component: str, template_path: str):
        """
        Deploys a component using the provided Bicep template.

        Args:
            component (str): Component name.
            template_path (str): Path to the Bicep template file.
        """
        deploy_name = context.get_deployment_name(conf['env_name'], component)
        rg_name = context.get_main_rg_name(conf['env_name'])
        params = __prepare_params(component, rg_name, conf)
        formatted_params = format_parameters_for_bicep(params)
        params_file_path = files.write_params_to_tempfile(tmp_dir_path, formatted_params)
        if bicep.deploy(deploy_name=deploy_name, template_file_path=template_path,
                     rg_name=rg_name, params_file_path =params_file_path ):
            log.info(f"Successfully deployed component: {component}")

    for group in parallel_groups:
        common_components = list(set(group) & set(sorted_components))
        if not common_components:
            continue

        with ThreadPoolExecutor() as executor:
            futures = []
            for component in common_components:
                template_file_name = core_deploy_files.get(component) or apps_deploy_files.get(component)
                template_file_path = os.path.join(bicep_dir_path, template_file_name)

                log.info(f"Deploying component: {component}")
                futures.append(executor.submit(deploy_component, component, template_file_path))
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log.error(f"Error deploying component: {component}")
                    log.error(e)

def __prepare_params(component: str, rg_name: str, conf: dict):
    if component == 'role':
        return __prepare_role_params(conf)
    elif component == 'sa':
        return __prepare_sa_params(conf)
    elif component == 'vnet':
        return __prepare_vnet_params(rg_name, conf)
    elif component == 'acr':
        return __prepare_acr_params(rg_name, conf) 
    elif component == 'keyvault':
        return __prepare_keyvault_params(rg_name, conf)
    elif component == 'dev_vm':
        return __prepare_dev_vmss_params(conf)
    elif component == 'db':
        return __prepare_sql_db_params(rg_name, conf)
    else:
        raise ValueError(f"Invalid component: {component}") 

def __prepare_role_params(conf: dict):
    env_name = conf['env_name']
    params = {}
    params['location'] = conf['location']
    params['vm_id_name'] = context.get_vm_id_name(env_name)
    params['backend_id_name'] = context.get_backend_id_name(env_name)
    params['frontend_id_name'] = context.get_frontend_id_name(env_name)
    params['schedule_id_name'] = context.get_scheduler_id_name(env_name)

    return params

def __prepare_sa_params(conf: dict):
    env_name = conf['env_name']
    rg_name = context.get_main_rg_name(env_name)
    params = {}
    sa = StorageAccount(conf['subscription_id'])
    sa_name = sa.find_storage_account_by_prefix(rg_name, env_name)
    if sa_name:
        params['storage_account_name'] = sa_name
    else:
        params['storage_account_name'] = context.get_unique_storage_account_name(env_name)

    params['dev_container_name'] = context.get_backend_id_name(env_name)
    params['vm_id_name'] = context.get_frontend_id_name(env_name)

    return params

def __prepare_vnet_params(rg_name: str, conf: dict):
    env_name = conf['env_name']
    vnet_cidr = conf['vnet_cidr']
    dev_subnet_cidr = conf['dev_subnet_cidr']
    vnet = Vnet(conf['subscription_id'])
    vnet_name = context.get_vnet_name(env_name)
    vnet_exists = vnet.get_vnet_by_name(rg_name, vnet_name)
    cidr_available = vnet.check_vnet_cidr_availability(vnet_cidr)
    if not ( vnet_exists or cidr_available):
        raise ValueError(f"Vnet does not exist, but VNet CIDR {vnet_cidr} is already in use.")
    
    params = {}
    params['vnet_name'] = context.get_vnet_name(env_name)
    params['vnet_cidr'] = vnet_cidr
    params['dev_subnet_name'] = context.get_dev_subnet_name(env_name)
    params['dev_subnet_cidr'] = dev_subnet_cidr
    
    return params

def __prepare_acr_params(rg_name: str, conf: dict):
    env_name = conf['env_name']
    params = {}
    acr = Acr(conf['subscription_id'])
    acr_name = acr.find_acr_by_prefix(rg_name, env_name)
    if acr_name:
        params['acr_name'] = acr_name
    else:
        params['acr_name'] = context.get_unique_acr_name(env_name)
    params['vm_id_name'] = context.get_vm_id_name(env_name)
    
    return params

def __prepare_keyvault_params(rg_name: str, conf: dict):
    params = {}
    env_name = conf['env_name']
    keyvault = Keyvault(conf['subscription_id'])
    keyvault_name = keyvault.find_keyvault_by_prefix(rg_name, env_name)
    if keyvault_name:
        params['keyvault_name'] = keyvault_name
        params['sql_pass'] = keyvault.get_sql_password_from_keyvault(keyvault_name, context.get_sql_secret_name(env_name))
    else:
        params['keyvault_name'] = context.get_unique_keyvault_name(env_name)
        params['sql_pass'] = keyvault.generate_password()
    params['sql_secret_name'] = context.get_sql_secret_name(env_name)
    
    return params

def __prepare_dev_vmss_params(conf: dict):
    params = {}
    env_name = conf['env_name']
    params['dev_vm_name'] = context.get_dev_vm_name(env_name)
    params['dev_vmss_name'] = context.get_dev_vmss_name(env_name)
    params['vm_id_name'] = context.get_vm_id_name(env_name)
    params['admin_username'] = conf['AdminUsername']
    params['admin_password'] = conf['AdminPassword']
    params['use_ssh'] = True if conf['UseSsh'].lower() == 'true' else False
    params['vm_size'] = conf['DevVmSize']
    params['ubuntu_os_version'] = conf['UbuntuOsVersion']
    params['vnet_name'] = context.get_vnet_name(env_name)
    params['subnet_name'] = context.get_dev_subnet_name(env_name)
    params['os_disk_type'] = conf['OsDiskType']
    
    return params

def __prepare_sql_db_params(rg_name: str, conf: dict):
    params = {}
    env_name = conf['env_name']
    rg_name = context.get_main_rg_name(env_name)
    sql_db = SqlDb(conf['subscription_id'])
    keyvault = Keyvault(conf['subscription_id'])

    sql_db_name  = sql_db.find_sql_db_by_prefix(rg_name, env_name)
    if sql_db_name:
        params['sql_db_name'] = sql_db_name
    else:
        params['sql_db_name'] = context.get_unique_sql_server_name(env_name)

    keyvault_name = keyvault.find_keyvault_by_prefix(rg_name, env_name)
    sql_pass = keyvault.get_sql_password_from_keyvault(keyvault_name, context.get_sql_secret_name(env_name))
    if not sql_pass:
        raise ValueError(f"SQL password not found in Key Vault {keyvault_name}")
    params['sql_pass'] = sql_pass
    params['db_name'] = conf['DbName']
    params['admin_name'] = conf['DbRootName']

def __prepare_app_container_params(rg_name: str, conf: dict):
    params = {}
    env_name = conf['env_name']
    acr = Acr(conf['subscription_id'])
    acr_name = acr.find_acr_by_prefix(rg_name, env_name)
    if not acr_name:
        raise ValueError(f"ACR not found for the environment {env_name}")
    params['acr_name'] = acr_name
    params['dev_container_name'] = context.get_backend_id_name(env_name)
    params['vm_id_name'] = context.get_vm_id_name(env_name)
    params['app_container_env_name'] = context.get_apps_container_env_name(env_name)

    return params


def __upload_vm_conf(conf: dict, params: dict):
    storage_account_name = params['storage_account_name']
    dev_container_name = params['dev_container_name']
    vm_conf_dir_path = os.path.join(conf['RootPath'], 'vm_conf')
    sa = StorageAccount(conf['subscription_id'])
    try:
        file_names = files.get_file_names(vm_conf_dir_path)
        for file_name in file_names:
            log.info(f"Uploading file {file_name} to the container {dev_container_name} in the storage account {storage_account_name}")
            file_path = os.path.join(vm_conf_dir_path, file_name)
            sa.upload_file_to_container(storage_account_name, dev_container_name, file_path)
    except Exception as e:
        log.error(f"An error occurred while uploading the VM configuration files: {e}")
        raise e

def format_parameters_for_bicep(input_dict):
    """
    Azure Bicep CLI 用にパラメータを整形する関数
    """
    return {key: {"value": value} for key, value in input_dict.items()}
