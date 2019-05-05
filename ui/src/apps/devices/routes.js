
const routes = [
  // Devices
  { path: 'devices/devices', component: () => import('./views/Devices') },
  { path: 'devices/devices/0/create_device', component: () => import('./views/DeviceCreate') },
  { path: 'devices/devices/:id', component: () => import('./views/DeviceDetails') },
  { path: 'devices/devices/:id/children', component: () => import('./views/DeviceChildren') },
  { path: 'devices/devices/:id/connect_logs', component: () => import('./views/DeviceDetailsConnect') },
  { path: 'devices/devices/:id/events', component: () => import('./views/DeviceDetailsEvents') },
  { path: 'devices/devices/:id/control', component: () => import('./views/DeviceDetailsControl') },
  { path: 'devices/devices/:id/capability_data', component: () => import('./views/CapabilityData') },
  // Groups
  { path: 'devices/groups', component: () => import('./views/Groups') },
  { path: 'devices/groups/:id', component: () => import('./views/GroupDetails') },
  // Security
  { path: 'security/certs', component: () => import('./views/Certs') },
  { path: 'security/certs/:id', component: () => import('./views/CertDetails') },
  // Gateway
  { path: '/devices/gateways/', component: () => import('./views/Gateways') },
  { path: '/devices/gateways/:id', component: () => import('./views/GatewayDetails') },
  { path: '/devices/gateways/:id/devices', component: () => import('./views/GatewayDevices') },
  { path: 'devices/gateways/:id/connect_logs', component: () => import('./views/GatewayDetailsConnect') },
  { path: '/devices/gateways/:id/events', component: () => import('./views/GatewayDetailsEvents') },
  { path: '/devices/gateways/:id/control', component: () => import('./views/GatewayDetailsControl') },
  { path: '/devices/gateways/:id/devices_data', component: () => import('./views/GatewayDetailsDevicesData') },
]

export default routes
