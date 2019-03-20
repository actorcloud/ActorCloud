import EmqSelect from '@/components/EmqSelect'
import EmqButton from '@/components/EmqButton'
import TabsCardHead from '@/components/TabsCardHead'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EditToggleButton from '@/components/EditToggleButton'
import variable from './variable'

// Function install
export default (Vue) => {
  Vue.component(EmqSelect.name, EmqSelect)
  Vue.component(EmqButton.name, EmqButton)
  Vue.component(TabsCardHead.name, TabsCardHead)
  Vue.component(EmqDetailsPageHead.name, EmqDetailsPageHead)
  Vue.component(EditToggleButton.name, EditToggleButton)
  Vue.prototype.$variable = variable
}
