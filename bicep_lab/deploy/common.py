core_deploy_files = {
    'vnet': 'vnet.bicep',
    'acr': 'acr.bicep',
    'sa': 'storageaccount.bicep',
    'keyvault': 'keyvault.bicep',
    'role': 'id.bicep',
    'dev_vm': 'dev_vm.bicep'
}

apps_deploy_files = {
    'db': 'db.bicep',
    'app_container': 'appcontainer.bicep',
    'front': 'front.bicep',
    'back': 'back.bicep',
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
