import { ResizeSensor } from 'css-element-queries'


export default {
  watch: {
    leftbar() {
      try {
        new ResizeSensor(document.querySelector('.leftbar'), () => {
          this.chart.resize()
        })()
      } catch (e) {
        return 0
      }
    },
  },

  mounted() {
    setTimeout(() => {
      window.addEventListener('resize', this.chart.resize)
    }, 200)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.chart.resize)
  },
}
