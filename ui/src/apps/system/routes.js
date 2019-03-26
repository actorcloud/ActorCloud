const routes = [
  {
    path: 'system_info',
    component: () => import('./views/SystemInfo'),
    meta: { requiresAdmin: true },
  },
  {
    path: 'logo_info',
    component: () => import('./views/Logo'),
    meta: { requiresAdmin: true },
  },
]

export default routes
