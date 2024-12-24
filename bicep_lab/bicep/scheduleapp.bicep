param env_name string
param acrName string
param ai_connection_string string
param imageTag string = 'latest'
param app_name string = 'schedule'
param location string = resourceGroup().location
param id_name string = 'id-${app_name}-${env_name}'

module roleAssign 'uid.bicep' = {
  name: 'roleAssign'
  params: {
    location: location
    acrName: acrName
    id_name: id_name
  }
}

resource containerappsEnv 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: env_name
  scope: resourceGroup()
}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: id_name
  scope: resourceGroup()
}

resource scheduleApp 'Microsoft.App/containerApps@2023-05-01' = {
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
        targetPort: 8083
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
          resources: {
            cpu: json('0.5')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: ai_connection_string 
            }
          ]
        }
      ]
      scale: {
        maxReplicas: 2
        minReplicas: 1
      }
    }
  }
}
