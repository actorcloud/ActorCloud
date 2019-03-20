#!/usr/bin/env node

// Get directory of apps
const fs = require('fs')
const path = require('path')

const root = path.join(`${__dirname}/src/apps`)

const getDirs = (path) => {
  return fs.readdirSync(path)
    .filter(p => !p.includes('.'))
}

const setApps = (dirs) => {
  fs.writeFile(
    './src/assets/micro.apps.json',
    JSON.stringify(dirs, null, 2),
      (err) => {
      if (err) {
        console.log(err)
      } else {
        console.log('👌 Get directory of apps successful!')
      }
    },
  )
}

setApps(getDirs(root))
