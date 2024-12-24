import os
import json
import docopt
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.identity import DefaultAzureCredential
from deploy import deploy_bicep_template
from deploy.utils.log import log
from deploy import resource_group

root_path = os.path.dirname(os.path.dirname(__file__))
bicep_template_path = os.path.join(root_path, 'bicep')
credential = DefaultAzureCredential()

core_deploy_files = {
    'vnet': 'vnet.bicep',
    'acr': 'acr.bicep',
    'sa': 'storageaccount.bicep',
    'keyvault': 'keyvault.bicep',
    'role': 'id.bicep',
    'dev_vm': 'dev_vm.bicep',
}
apps_deploy_files = {
    'db': 'sqldb.bicep',
    'app_container': 'appcontainer.bicep',
    'front': 'frontend.bicep',
    'back': 'backend.bicep',
    'scheduler': 'scheduler.bicep'
}

core_parallel_groups = [
    ['vnet', 'acr', 'sa', 'keyvault'],
    ['role'],
    ['dev_vm']
]

apps_parallel_groups = [
    ['db', 'app_container'],
    ['back', 'scheduler'],
    ['front']
]

all_components_with_order = list(core_deploy_files.keys()) + list(apps_deploy_files.keys())

def main():
    args = docopt.docopt(__read_usage())
    config = __read_config()
    # オプションのリストを作成
    options = [
        args['--core-deploy'], args['-cd'],
        args['--apps-deploy'], args['-ad'],
        args['--undeploy'], args['--destroy']
    ]

    # オプションがただ一つだけ含まれていることを確認
    if sum(bool(option) for option in options) != 1:
        log.error("Exactly one of the options must be specified.")
        raise ValueError("Exactly one of the options must be specified.")

    if args['--core-deploy'] or args['-cd'] or args['--apps-deploy'] or args['-ad']:
        deploy(args, config)
    elif args['--undeploy']:
        undeploy(args, config)
    elif args['--destroy']:
        destroy(args, config)
    else:
        log.error("Invalid option.")
        raise ValueError("Invalid option.")

def destroy(args, config):
    log.info("Destroying the resource group.")
    resource_group.delete_resource_group(credential, config['subscription_id'], config['resource_group_name'])

def undeploy(args, config):
    ## TOBE: Implement undeploy function
    pass

def deploy(args, config):
    args = docopt.docopt(__read_usage())
    config = __read_config()
    components = []
    if args['--core-deploy'] or args['-cd']:
        components = __get_valid_components(args['--components'], core_deploy_files)
    if args['--apps-deploy'] or args['-ad']:
        components = __get_valid_components(args['--components'], apps_deploy_files)
    
    __validate_resource_group(components, config)
    sorted_components = sorted(components, key=lambda x: all_components_with_order.index(x))
    parallel_groups = core_parallel_groups + apps_parallel_groups

    for group in parallel_groups:
        common_components = list(set(group) & set(sorted_components))
        if not common_components:
            continue

        with ThreadPoolExecutor() as executor:
            futures = []
            for component in common_components:
                template_file = core_deploy_files.get(component) or apps_deploy_files.get(component)
                template_path = os.path.join(bicep_template_path, template_file)
                log.info(f"Deploying component: {component}")
                futures.append(executor.submit(deploy_bicep_template, component, config, template_path))
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log.error(f"Error deploying component: {e}")

def __get_valid_components(raw_components_str, valid_components_dict):
    raw_components = raw_components_str.split(',')
    valid_components = list(valid_components_dict.keys())
    components = []
    for component in raw_components:
        if 'all' in raw_components:
            components = valid_components
            break
        if component not in valid_components:
            log.error(f'Invalid component: {component}')
            raise ValueError(f'Invalid component: {component}')
        components.append(component)
    return components

def __read_usage():
    with open(os.path.join(root_path, 'usage'), 'r') as usage_file:
        return usage_file.read().strip()

def __read_config():
    with open(os.path.join(root_path, 'config.yml'), 'r') as config_file:
        return yaml.safe_load(config_file)
    
def __validate_resource_group(components, config):
    resource_group_name = config['resource_group_name']
    subscription_id = config['subscription_id']
    location = config['location']
    if any([component in components for component in core_deploy_files.keys()]):
        resource_group.create_resource_group(subscription_id, resource_group_name, location)
    else:
        if not resource_group.check_resource_group_exists(credential, subscription_id, resource_group_name):
            log.error(f"Before deploying the application components, the resource group {resource_group_name} must exist.")
            raise ValueError(f"Before deploying the application components, the resource group {resource_group_name} must exist.")
        else:
            log.info(f"validated resource group {resource_group_name} ok.")

if __name__ == "__main__":
    main()
