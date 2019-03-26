
const routes = [
  { path: 'current_alerts', component: () => import('./views/CurrentAlerts') },
  { path: 'current_alerts/:id', component: () => import('./views/CurrentAlertDetails') },
  { path: 'history_alerts', component: () => import('./views/HistoryAlerts') },
  { path: 'history_alerts/:id', component: () => import('./views/HistoryAlertDetails') },
]

export default routes
