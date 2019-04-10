const routes = [
  { path: 'products', component: () => import('./views/Products') },
  { path: 'products/:id', component: () => import('./views/ProductDetails') },
  { path: 'products/:id/devices', component: () => import('./views/ProductDevices') },
  { path: 'products/:id/items', component: () => import('./views/ProductItems') },
  { path: 'products/:id/definition', component: () => import('./views/ProductDefinition') },
  { path: 'products/:id/definition/:streamID', component: () => import('./views/DataStreamDetails') },
  { path: 'products/:id/codec', component: () => import('./views/ProductCodec.vue') },
  { path: 'codec', component: () => import('./views/ProfileReviews.vue') },
]

export default routes
