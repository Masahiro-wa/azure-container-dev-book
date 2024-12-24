param env_name string
param acrName string
param vaultName string
param ai_connection_string string
param imageTag string
param app_name string
param id_name string = 'id-${app_name}-${env_name}'
param location string = resourceGroup().location

resource containerappsEnv 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: env_name
  scope: resourceGroup()
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: vaultName
  scope: resourceGroup()
}

resource scheduleApi 'Microsoft.App/containerApps@2023-05-01' existing = {
  name: 'schedule'
  scope: resourceGroup()
}

module roleAssign 'uid.bicep' = {
  name: 'roleAssign'
  params: {
    location: location
    acrName: acrName
    id_name: id_name
  }
}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: id_name
  scope: resourceGroup()
}

resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  dependsOn: [
    roleAssign
  ]
  name: app_name
  location: location
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerappsEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
      }
      registries: [
        {
          identity: userAssignedIdentity.id
          server: '${acrName}.azurecr.io'
        }
      ]
      secrets: [
        {
          name: 'ai-connection-string'
          value: ai_connection_string
        }
      ]
    }
    template: {
      containers: [
        {
          name: app_name
          image: '${acrName}.azurecr.io/${app_name}:${imageTag}'
          // K8sとは異なりここでリソース制限は設定できない
          resources: {
            cpu: json('1.0')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: 'ai-connection-string'
            }
            {
              name: 'schedule.api.url'
              value: 'https://${scheduleApi.properties.configuration.ingress.fqdn}/schedule'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  parent: keyVault
  name: 'add'
  properties: {
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: backendApp.identity.principalId
        permissions: {
          secrets: [
            'get'
            'list'
          ]
        }
      }
    ]
  }
}

output appFqdn string = backendApp.properties.configuration.ingress.fqdn
