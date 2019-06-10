const backendUrl = process.env.VUE_APP_SERVER || ''
const isProduction = process.env.NODE_ENV === 'production'

module.exports = {
  devServer: {
    port: 9999,
    proxy: {
      '/api/v1': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/backend_static': {
        target: `${backendUrl}/api/v1`,
        changeOrigin: true,
      },
    },
  },
  chainWebpack: config => {
    if (isProduction) {
      config.optimization.minimize(true)
      config.optimization.splitChunks({
        chunks: 'all'
      })
    }
  },
  // Disabled the production environment generates a sourceMap file
  productionSourceMap: false,
  css: {
    // Enable to use the css separation plugin ExtractTextPlugin
    extract: true,
    // Disable CSS source maps
    sourceMap: false,
    // Disabled CSS modules for all css / pre-processor files.
    modules: false,
  },
}
