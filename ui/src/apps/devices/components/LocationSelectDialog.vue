<template>
  <div class="location-select-dialog">
    <emq-dialog
      width="60%"
      :title="$t('devices.locationSelect')"
      :visible.sync="dialogVisible"
      @confirm="confirm">
      <div id="location-select-container" class="map" tabindex="0"></div>
      <div id="pickerBox">
        <input id="pickerInput" :placeholder="$t('devices.locationKey')" />
        <div id="poiInfo"></div>
      </div>
    </emq-dialog>
  </div>
</template>


<script>
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'location-select-dialog',
  components: { EmqDialog },

  props: {
    deviceLocation: {
      type: Array,
      default: () => {
        return [116.397477, 39.908692]
      },
    },
    confirm: {
      type: Function,
      required: true,
    },
  },

  data() {
    return {
      dialogVisible: false,
      position: {},
      positionPicker: undefined,
    }
  },

  methods: {
    /* eslint-disable */
    initMap() {
      const map = new AMap.Map('location-select-container', {
        center: this.position.lng === undefined ? this.deviceLocation : [this.position.lng, this.position.lat],
        zoom: 16,
      })
      AMapUI.loadUI(['misc/PoiPicker', 'misc/PositionPicker'], (PoiPicker, PositionPicker) => {
        const poiPicker = new PoiPicker({
          city: '全国',
          input: 'pickerInput',
        })
        // Drag to select the location
        this.positionPicker = new PositionPicker({
          mode: 'dragMarker',
          map: map,
        })
        this.positionPicker.on('success', (positionResult) => {
          this.position.lng = positionResult.position.lng
          this.position.lat = positionResult.position.lat
          this.position.name = positionResult.address
        })
        this.positionPicker.start()
        // Init poiPicker
        this.poiPickerReady(map, poiPicker)
      })
      map.addControl(new AMap.ToolBar()) // Tool bar
    },

    // Location search mark
    poiPickerReady(map, poiPicker) {
      window.poiPicker = poiPicker
      const marker = new AMap.Marker()
      const infoWindow = new AMap.InfoWindow({
        offset: new AMap.Pixel(0, -20),
      })
      // Picked a POI
      poiPicker.on('poiPicked', (poiResult) => {
        this.position = poiResult.item
        const source = poiResult.source
        const poi = poiResult.item
        const info = {
          source: source,
          id: poi.id,
          name: poi.name,
          location: poi.location.toString(),
          address: poi.address,
        }
        // marker.setMap(map)
        // infoWindow.setMap(map)
        marker.setPosition(poi.location)
        infoWindow.setPosition(poi.location)
        // infoWindow.setContent('POI信息: <pre>' + JSON.stringify(info, null, 2) + '</pre>')
        // infoWindow.open(map, marker.getPosition())
        map.setCenter(marker.getPosition())
        this.positionPicker.start()
      })
      poiPicker.onCityReady(() => {
        poiPicker.suggest('')
      })
    },
  },

  updated() {
    this.initMap()
  },
}
</script>


<style lang="scss">
.location-select-dialog {
  #location-select-container {
    height: 400px;
  }
  #pickerBox {
    position: absolute;
    z-index: 9999;
    top: 100px;
    right: 45px;
    width: 300px;
  }
  #pickerInput {
    width: 290px;
    padding: 5px 5px;
  }
  #poiInfo {
    background: #fff;
  }
  .amap_lib_placeSearch {
    .poibox.highlight {
      background-color: #CAE1FF;
    }
    .poi-more {
      display: none !important;
    }
  }
}
</style>
