param sql_name string
@secure()
param sql_pass string
param db_name string = 'backenddb'
param admin_name string = 'azureadmin'

@description('The tier of the SQL Database. High Availability is only available for the GeneralPurpose and MemoryOptimized tier.')
@allowed([
  'Burstable'
  'GeneralPurpose'
  'MemoryOptimized'
])
param serverTier string = 'Burstable'

@description('The SKU name of the SQL Database.The value depends on the selected Tier, so please refer to the official website.')
param skuName string = 'Standard_B1ms'

@description('Server version')
@allowed([
  '8.0.21'
])
param version string = '8.0.21'
param location string = resourceGroup().location

resource mySqlServer 'Microsoft.DBforMySQL/flexibleServers@2023-06-30' = {
  name: sql_name
  location: location
  properties: {
    administratorLogin: admin_name
    administratorLoginPassword: sql_pass
    version: version
    storage: {
      storageSizeGB: 32
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
  sku: {
    name: skuName
    tier: serverTier
  }
}

resource mainDb 'Microsoft.DBforMySQL/flexibleServers/databases@2023-06-30' = {
  name: db_name
  parent: mySqlServer
  properties: {
    charset: 'utf8'
    collation: 'utf8_general_ci'
  }
}
