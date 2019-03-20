const backendUrl = process.env.VUE_APP_SERVER || ''

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
}
