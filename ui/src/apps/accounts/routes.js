const routes = [
  { path: '/users/users', component: () => import('./views/Users') },
  { path: '/users/invitations', component: () => import('./views/Invitations') },
  { path: '/users/users/:id', component: () => import('./views/UserDetails') },
  { path: '/applications', component: () => import('./views/Applications') },
  { path: '/applications/:id', component: () => import('./views/ApplicationDetails') },
  { path: '/tenants', component: () => import('./views/Tenants') },
  { path: '/tenants/:id', component: () => import('./views/TenantDetails') },
  { path: '/roles', component: () => import('./views/UserRoles') },
  { path: '/roles/:id', component: () => import('./views/UserRoleDetails') },
  { path: '/app_roles', component: () => import('./views/AppRoles') },
  { path: '/app_roles/:id', component: () => import('./views/AppRoleDetails') },
  { path: '/login_logs', component: () => import('./views/LoginLogs') },
  { path: '/messages', component: () => import('./views/MessagesCenter') },
  { path: '/messages/:id', component: () => import('./views/MessageCenterDetails') },
]

export default routes
