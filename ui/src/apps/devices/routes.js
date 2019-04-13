
const routes = [
  // Devices
  { path: 'devices/devices', component: () => import('./views/Devices') },
  { path: 'devices/devices/0/create_device', component: () => import('./views/DeviceCreate') },
  { path: 'devices/devices/:id', component: () => import('./views/DeviceDetails') },
  { path: 'devices/devices/:id/children', component: () => import('./views/DeviceChildren') },
  { path: 'devices/devices/:id/security', component: () => import('./views/DeviceDetailsSecurity') },
  { path: 'devices/devices/:id/objects', component: () => import('./views/DeviceDetailsObjects') },
  { path: 'devices/devices/:id/items', component: () => import('./views/DeviceDetailsItems') },
  { path: 'devices/devices/:id/events', component: () => import('./views/DeviceDetailsEvents') },
  { path: 'devices/devices/:id/control', component: () => import('./views/DeviceDetailsControl') },
  { path: 'devices/devices/:id/capability_data', component: () => import('./views/CapabilityData') },
  // Groups
  { path: 'devices/groups', component: () => import('./views/Groups') },
  { path: 'devices/groups/:id', component: () => import('./views/GroupDetails') },
  { path: 'devices/groups/:id/subscriptions', component: () => import('./views/GroupProxySubscriptions') },
  { path: 'devices/groups/:id/control', component: () => import('./views/GroupControl') },
  { path: 'devices/groups/:id/metrics_data', component: () => import('./views/GroupMetricsData') },
  // Security
  { path: 'security/policies', component: () => import('./views/Policies') },
  { path: 'security/policies/:id', component: () => import('./views/PoliciesDetails') },
  { path: 'security/certs', component: () => import('./views/Certs') },
  { path: 'security/certs/:id', component: () => import('./views/CertDetails') },
  // Device log
  { path: 'device_logs/connect_logs', component: () => import('./views/DeviceConnectLogs') },
  { path: 'device_logs/control_logs', component: () => import('./views/DeviceControlLogs') },
  // Gateway
  { path: '/devices/gateways/', component: () => import('./views/Gateways') },
  { path: '/devices/gateways/:id', component: () => import('./views/GatewayDetails') },
  { path: '/devices/gateways/:id/devices', component: () => import('./views/GatewayDevices') },
  { path: '/devices/gateways/:id/events', component: () => import('./views/GatewayDetailsEvents') },
  { path: '/devices/gateways/:id/control', component: () => import('./views/GatewayDetailsControl') },
  { path: '/devices/gateways/:id/devices_data', component: () => import('./views/GatewayDetailsDevicesData') },
]

export default routes
