import MicroApps from '../assets/micro.apps.json'
import PrivateApps from '../assets/micro.private.json'

const stores = {}

// Capitalization
const lowerCamelCase = (str) => {
  const reg = /-(\w)/g
  return str.replace(reg, ($0, $1) => $1.toUpperCase())
}

// Add the attribute for store
const storeAssign = (app, store) => {
  const appName = lowerCamelCase(app)
  const hasStore = store.default && JSON.stringify(store.default) !== '{}'
  if (hasStore) {
    stores[appName] = store.default
  }
}

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const store = require(`./${app}/store`)
  storeAssign(app, store)
})

PrivateApps.forEach((app) => {
  // eslint-disable-next-line
  const context = require.context('../', true, /\private_apps/)
  const store = context(`./private_apps/${app}/store.js`)
  storeAssign(app, store)
})

export default stores
