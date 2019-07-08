import dateformat from 'dateformat'

const getNowTimetamp = (type) => {
  const date = new Date()
  const formatBySecond = (date) => {
    const tmp = Date.parse(date).toString().substr(0, 10)
    return parseInt(tmp, 10)
  }
  if (type === 'second') {
    return formatBySecond(date)
  }
  return date.getTime()
}

const getNowDate = (format = 'yyyy-mm-dd HH:MM:ss') => {
  return dateformat(new Date(), format)
}

export { getNowTimetamp, getNowDate }
