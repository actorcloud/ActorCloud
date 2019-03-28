const routes = [
  { path: '/mqtt_client', component: () => import('./views/MQTTClient') },
  { path: '/coap_client', component: () => import('./views/CoAP') },
]

export default routes
