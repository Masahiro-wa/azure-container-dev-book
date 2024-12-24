@secure()
param sqlPass string
param vaultName string
param location string = resourceGroup().location

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: vaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    tenantId: subscription().tenantId
  }
}

resource dbPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'sqlPassword'
  properties: {
    value: sqlPass
  }
}
