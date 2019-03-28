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

if (PrivateApps.length) {
  PrivateApps.forEach((app) => {
    // eslint-disable-next-line
    const enLang = require(`../private_apps/${app}/lang/en`)
    // eslint-disable-next-line
    const zhLang = require(`../private_apps/${app}/lang/zh_CN`)
    Object.assign(appsEnLang, enLang.default)
    Object.assign(appsZhLang, zhLang.default)
  })
}

export { appsEnLang, appsZhLang }
