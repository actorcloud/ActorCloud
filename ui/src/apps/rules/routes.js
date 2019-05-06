const routes = [
  { path: '/business_rules', component: () => import('./views/BusinessRules') },
  { path: '/business_rules/:id', component: () => import('./views/BusinessRuleDetails') },
  { path: '/scope_rules', component: () => import('./views/ScopeRules') },
  { path: '/scope_rules/:id', component: () => import('./views/ScopeRuleDetails') },
  { path: '/actions', component: () => import('./views/Actions') },
  { path: '/actions/:id', component: () => import('./views/ActionDetails') },
  { path: '/timer_publish', component: () => import('./views/TimerPublish') },
  { path: '/timer_publish/:id', component: () => import('./views/TimerPublishDetails') },
]

export default routes
