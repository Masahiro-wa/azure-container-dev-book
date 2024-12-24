param env_name string
param acrName string
param imageTag string
param app_name string
param id_name string = 'id-${app_name}-${env_name}'
param location string = resourceGroup().location

resource containerappsEnv 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: env_name
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

resource frontendApp 'Microsoft.App/containerApps@2023-05-01' = {
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
        targetPort: 3000
      }
      registries: [
        {
          identity: userAssignedIdentity.id
          server: '${acrName}.azurecr.io'
        }
      ]
    }
    template: {
      containers: [
        {
          name: app_name
          image: '${acrName}.azurecr.io/${app_name}:${imageTag}'
          resources: {
            cpu: json('1.0')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output frontFqdn string = frontendApp.properties.configuration.ingress.fqdn
