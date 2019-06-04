import { httpGet } from '@/utils/api'
import { mapActions } from 'vuex'

export const currentDevicesMixin = {

  data() {
    return {
      tempDevice: {},
    }
  },

  computed: {
    currentDevices() {
      return this.$store.state.devices.currentDevices
    },
    currentDevice: {
      get() {
        const currentDevices = JSON.parse(localStorage.getItem('currentDevices')) || []
        this.tempDevice = currentDevices.find(
          item => item.deviceIntID === parseInt(this.$route.params.id, 10),
        )
        return this.tempDevice
      },
      set(newVal) {
        this.tempDevice = newVal
      },
    },
  },

  methods: {
    ...mapActions(['STORE_DEVICES']),
    loadDevice() {
      httpGet(`/devices/${this.$route.params.id}`).then((res) => {
        this.localCache(res.data)
      })
    },
    localCache(cache) { // Cache to local
      const currentDevices = this.currentDevices.slice()
      const currentDevice = {
        deviceID: cache.deviceID,
        deviceName: cache.deviceName,
        deviceIntID: cache.id,
        cloudProtocol: cache.cloudProtocol,
        cloudProtocolLabel: cache.cloudProtocolLabel,
        productIntID: cache.productIntID,
        productID: cache.productID,
        token: cache.token,
        deviceUsername: cache.deviceUsername,
        upLinkSystem: cache.upLinkSystem,
        gatewayProtocol: cache.gatewayProtocol,
        gatewayProtocolLabel: cache.gatewayProtocolLabel,
      }
      this.currentDevice = currentDevice
      const hasExist = currentDevices.find(
        item => item.deviceIntID === cache.id,
      )
      if (!hasExist) { // Cache is added only when it is not in the cache
        currentDevices.push(currentDevice)
      }
      this.STORE_DEVICES({ currentDevices })
    },
    updateLocalCache(cache) { // Update local cache
      const currentDevices = this.currentDevices.slice()
      let itemIndex = 0
      currentDevices.forEach((item) => {
        if (item.deviceIntID === parseInt(this.record.id, 10)) { // Sync changes to the local cache
          itemIndex = currentDevices.indexOf(item)
        }
      })
      currentDevices.splice(itemIndex, 1, cache)
      this.STORE_DEVICES({ currentDevices })
    },
  },

  created() {
    // Only is the device details page
    const isDeviceDetails = this.$route.fullPath.split('/').length === 4
    if (!this.currentDevice && !isDeviceDetails) {
      this.loadDevice()
    }
  },
}

export default {}
