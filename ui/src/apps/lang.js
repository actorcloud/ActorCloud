import MicroApps from '../assets/micro.apps.json'

const appsZhLang = {}
const appsEnLang = {}

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const enLang = require(`./${app}/lang/en`)
  Object.assign(appsEnLang, enLang.default)
})

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const zhLang = require(`./${app}/lang/zh_CN`)
  Object.assign(appsZhLang, zhLang.default)
})

export { appsEnLang, appsZhLang }
