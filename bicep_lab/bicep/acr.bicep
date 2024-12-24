param acr_name string
param location string = resourceGroup().location
param vm_id_name string

@allowed([
    'Basic'
    'Classic'
    'Standard'
    'Premium'
])
param sku string = 'Basic'

resource vmUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
    name: vm_id_name
    scope: resourceGroup()
}

//enable adminUserEnabled for Container Apps
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acr_name
  location: location
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: true
  }
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, vmUserAssignedIdentity .id, 'AcrPush')
  scope: acr
  properties: {
    principalId: vmUserAssignedIdentity.properties.principalId
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')
  }
}
