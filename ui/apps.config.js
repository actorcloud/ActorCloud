#!/usr/bin/env node

// Get directory of apps
const fs = require('fs')
const path = require('path')

const getAppsDirs = () => {
  const fsExistsSync = (path) => {
    try {
      fs.accessSync(path)
    } catch (e) {
      return false
    }
    return true
  }

  const dirs = {}

  const appsRoot = path.join(`${__dirname}/src/apps`)
  dirs.apps = fs.readdirSync(appsRoot)
    .filter(p => !p.includes('.'))

  const privateRoot = path.join(`${__dirname}/src/private_apps`)
  if (fsExistsSync(privateRoot)) {
    dirs.private = fs.readdirSync(privateRoot)
      .filter(p => !p.includes('.'))
  }
  return dirs
}

const setApps = (dirs) => {
  fs.writeFile(
    './src/assets/micro.apps.json',
    JSON.stringify(dirs.apps),
    (err) => {
      if (err) {
        console.log(err)
      } else {
        fs.writeFile(
          './src/assets/micro.private.json',
          JSON.stringify(dirs.private || []),
          (err) => {
            if (err) {
              console.log(err)
            }
            console.log('✅ Get apps successfully')
          },
        )
      }
    },
  )
}

setApps(getAppsDirs())
