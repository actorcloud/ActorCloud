import MicroApps from '../assets/micro.apps.json'

// Capitalization
const lowerCamelCase = (str) => {
  const reg = /-(\w)/g
  return str.replace(reg, ($0, $1) => $1.toUpperCase())
}

const stores = {}
MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const store = require(`./${app}/store`)
  const appName = lowerCamelCase(app)
  const hasStore = store.default && JSON.stringify(store.default) !== '{}'
  if (hasStore) {
    stores[appName] = store.default
  }
})

export default stores
