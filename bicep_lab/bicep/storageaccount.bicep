param storage_account_name string
param location string = resourceGroup().location
param sku string = 'Standard_LRS'
param dev_container_name string
param vm_id_name string

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storage_account_name
  location: location
  sku: {
    name: sku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = {
  parent: storageAccount
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = {
  parent: blobService
  name: dev_container_name
  properties: {}
}

resource vmUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: vm_id_name
  scope: resourceGroup()
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, vmUserAssignedIdentity.id, 'Storage Blob Data Reader')
  scope: storageAccount
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Reader
    principalId: vmUserAssignedIdentity.properties.principalId
  }
}
