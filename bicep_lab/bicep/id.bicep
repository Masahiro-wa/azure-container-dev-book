// param location string = resourceGroup().location
param location string
param vm_id_name string
param schedule_id_name string
param backend_id_name string
param frontend_id_name string

resource  vmUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: vm_id_name
  location: location
}

resource scheduleUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: schedule_id_name
  location: location
}

resource backendUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: backend_id_name
  location: location
}

resource frontendUserAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: frontend_id_name
  location: location
}
