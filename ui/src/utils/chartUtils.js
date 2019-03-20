export default {}

export function hex2rgba(hex, alpha) {
  const BASE = 16
  const HEX_REGEX = /^#?[a-fA-F0-9]+$/
  const HEX_SHORTHAND_LENGTH = 3
  const HEX_LENGTH = 6

  if (!HEX_REGEX.test(hex)) {
    throw Error('invalid hexadecimal')
  }

  if (hex[0] === '#') {
    hex = hex.slice(1)
  }

  if (hex.length === HEX_SHORTHAND_LENGTH) {
    hex = hex.split('')
    hex.splice(2, 0, hex[2])
    hex.splice(1, 0, hex[1])
    hex.splice(0, 0, hex[0])
    hex = hex.join('')
  }

  if (hex.length !== HEX_LENGTH) {
    throw Error('invalid hexadecimal length')
  }

  const values = [
    parseInt(hex.slice(0, 2), BASE),
    parseInt(hex.slice(2, 4), BASE),
    parseInt(hex.slice(4, 6), BASE),
  ]

  alpha = typeof alpha === 'number' ? alpha : parseFloat(alpha)
  if (alpha >= 0 && alpha <= 1) {
    values.push(alpha)
  } else {
    values.push(1)
  }

  return `rgba( ${values.join(',')} )`
}
