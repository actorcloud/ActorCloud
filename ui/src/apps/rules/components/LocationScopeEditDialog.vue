<template>
  <div class="location-scope-edit-dialog">
    <emq-dialog
      width="60%"
      :title="$t('scopes.scopeEdit')"
      :visible.sync="dialogVisible"
      @confirm="confirm">
      <el-popover
        placement="right"
        width="360"
        trigger="hover">
        <p>{{ editTip }}</p>
        <template slot="reference">
          <a href="javascript:;" class="location-question">
            <i class="el-icon-question" style="color: #889;"></i>
          </a>
        </template>
      </el-popover>
      <div id="tip">
        <input
          id="keyword"
          type="text"
          name="keyword"
          :value="$t('scopes.enterKeyword')"
          onfocus='this.value=""' />
      </div>
      <div id="location-scope-edit" class="map" tabindex="0"></div>
      <div class="button-group">
        <input
          type="button"
          :value="$t('scopes.resetScope')"
          class="scope-btn"
          @click="resetScope" />
        <input
          v-show="showButton === 'create'"
          id="circle"
          type="button"
          class="scope-btn"
          :value="$t('scopes.circleScope')" />
        <input
          v-show="showButton === 'create'"
          id="polygon"
          type="button"
          class="scope-btn"
          :value="$t('scopes.polygonScope')" />
      </div>
    </emq-dialog>
  </div>
</template>


<script>
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'location-scope-edit-dialog',
  components: {
    EmqDialog,
  },

  props: {
    deviceLocation: {
      type: Array,
    },
    locationScope: {
      type: Array,
      required: true,
    },
    clearLocationScope: {
      type: Function,
      required: true,
    },
    confirm: {
      type: Function,
      required: true,
    },
  },

  data() {
    return {
      dialogVisible: false,
      showButton: 'create',
      type: undefined,
      center: [116.397477, 39.908692],
      map: undefined,
      scope: [],
      editor: {},
      editTip: this.$t('scopes.scopeTips'),
    }
  },

  watch: {
    locationScope() {
      this.scope = this.locationScope
    },
  },

  methods: {
    resetScope() {
      this.dialogVisible = false
      this.clearLocationScope()
      this.editor = {}
      this.scope = []
      this.amapInit()
      this.dialogVisible = true
    },

    /* eslint-disable */
    amapInit() {
      if (this.deviceLocation.length !== 0) {
        this.center = this.deviceLocation
      }
      const windowsArr = []
      const marker = []
      this.map = new window.AMap.Map('location-scope-edit', {
        // zIndex: 100,
        zoom: 13,
        resizeEnable: true,
        center: this.center,
      })
      // Mark device location
      // const marker = new AMap.Marker({
      //   position: this.deviceLocation,
      // })
      // this.map.add(marker)

      //  Location keyword search
      AMap.plugin(['AMap.Autocomplete','AMap.PlaceSearch'], (map = this.map) => {
        const autoOptions = {
          // zIndex: 10000,
          city: this.$t('scopes.beijing'),
          input: 'keyword',
        }
        const autocomplete= new AMap.Autocomplete(autoOptions)
        const placeSearch = new AMap.PlaceSearch({
          city: this.$t('scopes.beijing'),
          map: map,
        })
        AMap.event.addListener(autocomplete, 'select', (e) => {
          // TODO: Implement your own functionality for the selected poi
          placeSearch.setCity(e.poi.adcode)
          placeSearch.search(e.poi.name)
        })
      })

      // A list of search results
      if (typeof this.map !== 'undefined') {
        this.map.on('complete', function() {
          if (location.href.indexOf('guide=1') !== -1) {
            this.map.setStatus({
              scrollWheel: false
            })
            if (location.href.indexOf('litebar=0') === -1) {
              this.map.plugin(['AMap.ToolBar'], function() {
                const options = {
                  liteStyle: true
                }
                if (location.href.indexOf('litebar=1') !== -1) {
                  options.position = 'LT'
                  options.offset = new AMap.Pixel(10, 40)
                } else if (location.href.indexOf('litebar=2') !== -1) {
                  options.position = 'RT'
                  options.offset = new AMap.Pixel(20, 40)
                } else if (location.href.indexOf('litebar=3') !== -1) {
                  options.position = 'LB'
                } else if (location.href.indexOf('litebar=4') !== -1) {
                  options.position = 'RB'
                }
                this.map.addControl(new AMap.ToolBar(options))
              })
            }
          }
        })
      }

      this.map.addControl(new AMap.ToolBar()) // Tool bar
      this.createScope(this.map)
      this.editScope(this.map)
    },

    createScope(map) {
      const mouseTool = new AMap.MouseTool(map) // Add the MouseTool plug-in to the map
      // Drawing circle
      AMap.event.addDomListener(document.getElementById('circle'), 'click', () => {
        this.type = 'circle'
        mouseTool.circle()
        AMap.event.addListener(mouseTool, 'draw', (e) => {
          this.scope = [[e.obj.getCenter().lng, e.obj.getCenter().lat], e.obj.getRadius() / 1000]
        })
      }, false)
      // Drawing polygon
      AMap.event.addDomListener(document.getElementById('polygon'), 'click', () => {
        this.type = 'polygon'
        mouseTool.polygon()
        AMap.event.addListener(mouseTool, 'draw', (e) => {
          this.scope = []
          e.obj.getPath().forEach((point) => {
            this.scope.push([point.lng, point.lat])
          })
        })
      }, false)
    },

    editScope(map) {
      /* eslint-disable */
      if (this.scope.length === 0) { // No scope
        this.showButton = 'create'
      } else if (this.scope.length === 2) { // Circle scope
        this.showButton = 'circle'
        this.editor.circle = (() => {
          const circle = new AMap.Circle({
            center: this.scope[0],
            radius: this.scope[1] * 1000,
            strokeOpacity: 1,
            strokeWeight: 3,
            fillColor: '#89b283',
            fillOpacity: 0.35,
          })
          circle.setMap(map)
          return circle
        })()
        map.setFitView()
        this.editor.circleEditor= new window.AMap.CircleEditor(map, this.editor.circle)
        this.editor.circleEditor.open()
      } else if (this.scope.length >= 3) { // Polygon scope
        this.showButton = 'polygon'
        this.editor.polygon = (() => {
          return new AMap.Polygon({
            map: map,
            path: this.scope,
            strokeOpacity: 1,
            strokeWeight: 3,
            fillColor: '#89b283',
            fillOpacity: 0.35,
          })
        })()
        map.setFitView()
        this.editor.polygonEditor= new window.AMap.PolyEditor(map, this.editor.polygon)
        this.editor.polygonEditor.open()
      }
    },

    closeEdit() {
      if (this.scope.length === 2 && this.editor.circleEditor) {
        this.editor.circleEditor.close()
        this.scope = [
          [this.editor.circle.getCenter().lng, this.editor.circle.getCenter().lat],
          this.editor.circle.getRadius() / 1000
        ]
      } else if (this.scope.length >= 3 && this.editor.polygonEditor) {
        this.editor.polygonEditor.close()
        this.scope = []
        this.editor.polygon.getPath().forEach((point) => {
          this.scope.push([point.lng, point.lat])
        })
      }
    },
  },

  updated() {
    this.amapInit()
  },
}
</script>


<style lang="scss">
.location-scope-edit-dialog {
  .emq-dialog .el-dialog__body {
    padding: 10px 20px 10px;
  }
  #location-scope-edit {
    height: 400px;
  }
  .button-group {
    margin-top: 25px;
  }
  .emq-dialog .el-dialog__footer {
    padding: 0px 20px 20px;
    margin-top: -35px;
  }
  #tip {
    background-color: #ddf;
    color: #333;
    border: 1px solid silver;
    position: absolute;
    top: 120px;
    right: 40px;
    overflow: hidden;
    line-height: 20px;
    z-index: 1024;
  }
  #tip input[type="text"] {
    height: 25px;
    border: 0;
    padding-left: 5px;
    width: 280px;
    border-radius: 3px;
    outline: none;
  }
  .location-question {
    position: absolute;
    top: 19px;
  }
}

html {
  &:lang(en) {
    .location-question {
      left: 115px;
    }
  }
  &:lang(zh) {
    .location-question {
      left: 100px;
    }
  }
}

.amap-sug-result {
  z-index: 10024 !important;
}
</style>
