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
    loadDevice() { // 加载当前设备
      httpGet(`/devices/${this.$route.params.id}`).then((res) => {
        this.localCache(res.data)
      })
    },
    localCache(cache) { // 缓存到本地
      const currentDevices = this.currentDevices.slice()
      const currentDevice = {
        deviceID: cache.deviceID,
        deviceName: cache.deviceName,
        deviceIntID: cache.id,
        cloudProtocol: cache.cloudProtocol,
        cloudProtocolLabel: cache.cloudProtocolLabel,
        productIntID: cache.productIntID,
        productID: cache.productID,
        deviceType: cache.deviceType,
        deviceTypeLabel: cache.deviceTypeLabel,
        token: cache.token,
        deviceUsername: cache.deviceUsername,
        upLinkSystem: cache.upLinkSystem,
      }
      this.currentDevice = currentDevice
      const hasExist = currentDevices.find(
        item => item.deviceIntID === cache.id,
      )
      if (!hasExist) { // 缓存中没有该设备时才加入缓存
        currentDevices.push(currentDevice)
      }
      this.STORE_DEVICES({ currentDevices })
    },
    updateLocalCache(cache) { // 更新本地缓存
      const currentDevices = this.currentDevices.slice()
      let itemIndex = 0
      currentDevices.forEach((item) => {
        if (item.deviceIntID === parseInt(this.record.id, 10)) { // 修改成功后，同步修改本地缓存
          itemIndex = currentDevices.indexOf(item)
        }
      })
      currentDevices.splice(itemIndex, 1, cache)
      this.STORE_DEVICES({ currentDevices })
    },
  },

  created() {
    // 判断是否是设备详情页面
    const isDeviceDetails = this.$route.fullPath.split('/').length === 4
    if (!this.currentDevice && !isDeviceDetails) {
      this.loadDevice()
    }
  },
}

export default {}
