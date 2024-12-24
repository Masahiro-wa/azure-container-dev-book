
param dev_vm_name string
param dev_vmss_name string
param vm_id_name string
param location string = resourceGroup().location
param admin_username string = 'azureadmin'
param use_ssh bool = true
@description('List of SSH public keys')
param ssh_public_keys array = [
  loadTextContent('../ssh_keys/authorized_keys.ubuntu')
]
var cloudInit = base64(loadTextContent('../cloud-init/docker-init.yml'))
@description('Type of Authentication')
@allowed([
    'sshPublicKey'
    'password'
])
param authentication_type string = 'sshPublicKey'
param admin_ssh_key string = ssh_public_keys[0]
@secure()
param admin_password string
param vnet_name string
param subnet_name string
param vm_nsg_name string
@description('Type of Security')
@allowed([
    'Standard'
    'TrustedLaunch'
])
param security_type string = 'Standard'
param os_disk_type string = 'Standard_LRS'
param vm_size string = 'Standard_D2s_v3'
param ubuntu_os_version string = 'Ubuntu-2204'
var imageReference = {
  'Ubuntu-2004': {
    publisher: 'Canonical'
    offer: '0001-com-ubuntu-server-focal'
    sku: '20_04-lts-gen2'
    version: 'latest'
  }
  'Ubuntu-2204': {
    publisher: 'Canonical'
    offer: '0001-com-ubuntu-server-jammy'
    sku: '22_04-lts-gen2'
    version: 'latest'
  }
}
// var publicIpAddressName = '${dev_vm_name}-pip'
// var networkInterfaceName = '${dev_vm_name}-nic'

var ssh_public_keysForAzureAdmin = [
  for key in ssh_public_keys: {
    path: '/home/azureadmin/.ssh/authorized_keys'
    keyData: key
  }
]
var ssh_public_keysForUbuntu = [
  for key in ssh_public_keys: {
    path: '/home/ubuntu/.ssh/authorized_keys'
    keyData: key
  }
]
var linuxConfiguration = {
  disablePasswordAuthentication: authentication_type == 'sshPublicKey'
  provisionVMAgent: true
  ssh: {
    publicKeys: concat(ssh_public_keysForAzureAdmin, ssh_public_keysForUbuntu)
  }
}
var securityProfileJson = {
  uefiSettings: {
    secureBootEnabled: true
    vTpmEnabled: true
  }
  securityType: security_type
}

resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' existing = {
  name: vnet_name
  scope: resourceGroup()
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' existing = {
  name: subnet_name
  parent: vnet
}

// resource publicIp 'Microsoft.Network/publicIPAddresses@2021-02-01' = {
//   name: publicIpAddressName
//   location: location
//   properties: {
//     publicIPAllocationMethod: 'Static'
//   }
// }

resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: vm_nsg_name
  location: location
  properties: {
    securityRules: [
      {
        name: 'SSH'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          direction: 'Inbound'
          priority: 100
          description: 'Allow SSH'
      }
    }
  ]
  }
}

// resource networkInterface 'Microsoft.Network/networkInterfaces@2022-05-01' = {
//   name: networkInterfaceName
//   location: location
//   properties: {
//     ipConfigurations: [
//       {
//         name: 'ipconfig1'
//         properties: {
//           subnet: {
//             id: subnet.id
//           }
//           privateIPAllocationMethod: 'Dynamic'
//           publicIPAddress: {
//             id: publicIp.id
//           }
//         }
//       }
//     ]
//     networkSecurityGroup: {
//       id: networkSecurityGroup.id
//     }
//   }
// }

// resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
//   name: dev_vm_name
//   location: location
//   identity: {
//     type: 'SystemAssigned'
//   }
//   properties: {
//     hardwareProfile: {
//       vmSize: vm_size
//     }
//     storageProfile: {
//       osDisk: {
//         createOption: 'FromImage'
//         diskSizeGB: 30
//         managedDisk: {
//           storageAccountType: os_disk_type
//         }
//       }
//       imageReference: imageReference[ubuntu_os_version]
//     }
//     osProfile: {
//       computerName: dev_vm_name
//       admin_username: admin_username
//       adminPassword: use_ssh ? admin_ssh_key : admin_password
//       linuxConfiguration: linuxConfiguration
//       customData: cloudInit
//     }
//     networkProfile: {
//       networkInterfaces: [
//         {
//           id: networkInterface.id
//         }
//       ]
//     }
//     securityProfile: ((security_type == 'TrustedLaunch') ? securityProfileJson : null)
//   }
// }

resource vmss 'Microsoft.Compute/virtualMachineScaleSets@2024-07-01' = {
  name: dev_vmss_name
  location: location
  sku: {
    tier: 'Standard'
    capacity: 1
  }
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${vm_id_name}': {}
    }
  }
  properties: {
    skuProfile: {
      vmSizes: [{name: vm_size}]
    }
    upgradePolicy: {
      mode: 'Manual'
    }
    virtualMachineProfile: {
      securityProfile: ((security_type == 'TrustedLaunch') ? securityProfileJson : null)
      storageProfile: {
        osDisk: {
          createOption: 'FromImage'
          diskSizeGB: 32
          managedDisk: {
            storageAccountType: os_disk_type
          }
        }
        imageReference: imageReference[ubuntu_os_version]
      }
      osProfile: {
        computerNamePrefix: dev_vm_name
        adminUsername: admin_username
        adminPassword: use_ssh ? admin_ssh_key : admin_password
        linuxConfiguration: linuxConfiguration
        customData: cloudInit
      }
      networkProfile: {
        networkInterfaceConfigurations: [
          {
            name: '${dev_vmss_name}-nic'
            properties: {
              primary: true
              ipConfigurations: [
                {
                  name: '${dev_vmss_name}-ipconfig'
                  properties: {
                    subnet: {
                      id: subnet.id
                    }
                  publicIPAddressConfiguration: {name: '${dev_vm_name}-pip', sku: {name: 'Standard'}}
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }
}

output dev_vmss_name string = vmss.name
output vmssConfigs array = vmss.properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations
