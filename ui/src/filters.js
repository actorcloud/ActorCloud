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
