import os
import docopt
import traceback
import yaml
from deploy.resources import ResourceGroup, Subscription
from deploy.utils import context, log
import deploy.deployment_manager as deployment_manager
from deploy.common import core_deploy_files, apps_deploy_files

log.set_console_handler('INFO')
root_path = os.path.dirname(__file__)
all_components_with_order = list(core_deploy_files.keys()) + list(apps_deploy_files.keys())

def main():
    args = docopt.docopt(__read_usage())
    config = __read_config()
    config['RootPath'] = root_path
    # オプションのリストを作成
    options = [
        args.get('--core-deploy', False), args.get('--apps-deploy', False),
        args.get('--undeploy', False), args.get('--destroy', False)
    ]

    # オプションがただ一つだけ含まれていることを確認
    if sum(bool(option) for option in options) != 1:
        log.error("Exactly one of the options must be specified.")
        raise ValueError("Exactly one of the options must be specified.")
    
    if not __confirm_user_input(args, config):
        return

    if args.get('--core-deploy', False) or args.get('--apps-deploy', False):
        deploy(args, config)
    elif args.get('--undeploy', False):
        undeploy(args, config)
    elif args.get('--destroy', False):
        destroy(args, config)
    else:
        log.error("Invalid option.")
        raise ValueError("Invalid option.")

def destroy(args, config):
    log.info("Destroying the resource group.")
    rg = ResourceGroup(config['subscription_id'])
    rg.delete_resource_group(context.get_main_rg_name(config['env_name']))

def undeploy(args, config):
    ## TOBE: Implement undeploy function
    pass

def deploy(args, config):
    components = []
    try:
        if args.get('--core-deploy', False):
            components = __get_valid_components(args['--components'], core_deploy_files)
        if args.get('--apps-deploy', False):
            components = __get_valid_components(args['--components'], apps_deploy_files)
        
        __validate_resource_group(components, config)
        sorted_components = sorted(components, key=lambda x: all_components_with_order.index(x))
        deployment_manager.run_deployment(config, sorted_components)
    except Exception as e:
        log.error(f"Error deploying the components: {e}")
        log.error(traceback.format_exc())
        raise e

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
    with open(os.path.join(root_path, 'deploy', 'usage'), 'r') as usage_file:
        return usage_file.read().strip()

def __read_config():
    with open(os.path.join(root_path, 'config', 'config.yml'), 'r') as config_file:
        return yaml.safe_load(config_file)
    
def __validate_resource_group(components, config):
    rg_name = context.get_main_rg_name(config['env_name'])
    location = config['location']
    resource_group = ResourceGroup(config['subscription_id'])

    if any([component in components for component in core_deploy_files.keys()]):
        resource_group.create_resource_group(rg_name, location)
    else:
        if not resource_group.check_resource_group_exists(rg_name):
            log.error(f"Before deploying the application components, the resource group {rg_name} must exist.")
            raise ValueError(f"Before deploying the application components, the resource group {rg_name} must exist.")
        else:
            log.info(f"validated resource group {rg_name} ok.")

def __confirm_user_input(args:dict, config: dict):
    subscription = Subscription(config['subscription_id'])
    sub_info = subscription.get_subscription_info()
    log.info(f"Subscription ID: {sub_info['id']}")
    log.info(f"Subscription Name: {sub_info['name']}")
    log.info(f"Tenant ID: {sub_info['tenant_id']}")
    log.info(f"Componets: {args['--components']}")
    confirm = input("Would you like to proceed with the deployment? (yes/y to confirm): ").strip().lower()
    if confirm != 'yes' and confirm != 'y':
        log.info("Deployment cancelled.")
        return False
    return True

if __name__ == "__main__":
    main()
