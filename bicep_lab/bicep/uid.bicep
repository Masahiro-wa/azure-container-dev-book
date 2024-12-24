param acrName string
param id_name string
param location string

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
  scope: resourceGroup()
}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: id_name
  location: location
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, userAssignedIdentity.id, 'AcrPush')
  scope: acr
  properties: {
    principalType: 'ServicePrincipal'
    principalId: userAssignedIdentity.properties.principalId
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4a94-bc8f-2d5f1a8b9e4c')
  }
}

output identityResourceName string = userAssignedIdentity.name
