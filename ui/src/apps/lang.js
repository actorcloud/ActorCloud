import MicroApps from '../assets/micro.apps.json'
import PrivateApps from '../assets/micro.private.json'

const appsZhLang = {}
const appsEnLang = {}

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const enLang = require(`./${app}/lang/en`)
  // eslint-disable-next-line
  const zhLang = require(`./${app}/lang/zh_CN`)
  Object.assign(appsEnLang, enLang.default)
  Object.assign(appsZhLang, zhLang.default)
})

PrivateApps.forEach((app) => {
  // eslint-disable-next-line
  const context = require.context('../', true, /\private_apps/)

  const enLang = context(`./private_apps/${app}/lang/en.js`)
  if (enLang.default) {
    Object.assign(appsEnLang, enLang.default)
  }
  const zhLang = context(`./private_apps/${app}/lang/zh_CN.js`)
  if (zhLang.default) {
    Object.assign(appsZhLang, zhLang.default)
  }
})

export { appsEnLang, appsZhLang }
