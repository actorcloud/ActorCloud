import lang from '@/lang'
import store from '@/store'

const dateformat = require('dateformat')

function pluralize(time, label) {
  if (time === 1) {
    return time + label
  }
  return `${time} ${label} s`
}

export function timeAgo(time) {
  const between = (Date.now() / 1000) - Number(time)
  if (between < 3600) {
    return pluralize(Math.floor(between / 60), ' minute')
  }
  if (between < 86400) {
    return pluralize(Math.floor(between / 3600), ' hour')
  }
  return pluralize(Math.floor(between / 86400), ' day')
}

export function dateFormat(date, format) {
  if (!date) {
    return false
  }
  return dateformat(date, format || 'yyyy-mm-dd HH:MM:ss')
}

// Translation system default role name
export const convertRoleName = (name) => {
  const locale = store.state.accounts.lang
  const $t = lang[locale]
  const roleNameDict = [
    'super_admin_role',
    'company_role',
    'personal_role',
    'system_user_role',
    'common_user_role',
    'device_user_role',
    'admin_app_role',
    'display_app_role',
    'device_app_role',
  ]
  return roleNameDict.includes(name) ? $t.roles[name] : name
}
