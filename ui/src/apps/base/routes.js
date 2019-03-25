
const routes = [
  { path: '', component: () => import('./views/Dashboard') },
  { path: 'forbidden', component: () => import('./views/403') },
]

export default routes
