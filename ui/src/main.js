import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import VueI18n from 'vue-i18n'
import ElementLocale from 'element-ui/lib/locale'
import 'element-ui/lib/theme-chalk/index.css'
import '@/assets/scss/element-variables.scss'
import 'material-design-icons/iconfont/material-icons.css'
import VueAMap, { lazyAMapApiLoaderInstance } from 'vue-amap'
import {
  Pagination,
  Dialog,
  Autocomplete,
  Dropdown,
  DropdownMenu,
  DropdownItem,
  Menu,
  Submenu,
  MenuItem,
  MenuItemGroup,
  Input,
  InputNumber,
  Radio,
  RadioGroup,
  RadioButton,
  Checkbox,
  CheckboxButton,
  CheckboxGroup,
  Switch,
  Select,
  Option,
  OptionGroup,
  Button,
  ButtonGroup,
  Table,
  TableColumn,
  DatePicker,
  TimeSelect,
  TimePicker,
  Popover,
  Tooltip,
  Breadcrumb,
  BreadcrumbItem,
  Form,
  FormItem,
  Tabs,
  TabPane,
  Tag,
  Tree,
  Alert,
  // Slider,
  Icon,
  Row,
  Col,
  Upload,
  Progress,
  Badge,
  Card,
  // Rate,
  Steps,
  Step,
  // Carousel,
  // CarouselItem,
  // Collapse,
  // CollapseItem,
  Cascader,
  // ColorPicker,
  // Transfer,
  // Container,
  // Header,
  Aside,
  // Main,
  // Footer,
  Loading,
  MessageBox,
  Message,
  // Notification,
} from 'element-ui'

import App from '@/App'
import store from '@/store'
import router from '@/router'
import lang from '@/lang'
import * as filters from '@/filters'
import installer from '@/utils/installer'

Vue.use(Pagination)
Vue.use(Dialog)
Vue.use(Autocomplete)
Vue.use(Dropdown)
Vue.use(DropdownMenu)
Vue.use(DropdownItem)
Vue.use(Menu)
Vue.use(Submenu)
Vue.use(MenuItem)
Vue.use(MenuItemGroup)
Vue.use(Input)
Vue.use(InputNumber)
Vue.use(Radio)
Vue.use(RadioGroup)
Vue.use(RadioButton)
Vue.use(Checkbox)
Vue.use(CheckboxButton)
Vue.use(CheckboxGroup)
Vue.use(Switch)
Vue.use(Select)
Vue.use(Option)
Vue.use(OptionGroup)
Vue.use(Button)
Vue.use(ButtonGroup)
Vue.use(Table)
Vue.use(TableColumn)
Vue.use(DatePicker)
Vue.use(TimeSelect)
Vue.use(TimePicker)
Vue.use(Popover)
Vue.use(Tooltip)
Vue.use(Breadcrumb)
Vue.use(BreadcrumbItem)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Tabs)
Vue.use(TabPane)
Vue.use(Tag)
Vue.use(Tree)
Vue.use(Alert)
// Vue.use(Slider)
Vue.use(Icon)
Vue.use(Row)
Vue.use(Col)
Vue.use(Upload)
Vue.use(Progress)
Vue.use(Badge)
Vue.use(Card)
// Vue.use(Rate)
Vue.use(Steps)
Vue.use(Step)
// Vue.use(Carousel)
// Vue.use(CarouselItem)
// Vue.use(Collapse)
// Vue.use(CollapseItem)
Vue.use(Cascader)
// Vue.use(ColorPicker)
// Vue.use(Transfer)
// Vue.use(Container)
// Vue.use(Header)
Vue.use(Aside)
// Vue.use(Main)
// Vue.use(Footer)

Vue.use(Loading.directive)

Vue.prototype.$loading = Loading.service
Vue.prototype.$msgbox = MessageBox
Vue.prototype.$alert = MessageBox.alert
Vue.prototype.$confirm = MessageBox.confirm
Vue.prototype.$prompt = MessageBox.prompt
// Vue.prototype.$notify = Notification
Vue.prototype.$message = Message

Vue.use(VueI18n)
Vue.use(VueAMap)
Vue.use(installer)

// register global utility filters.
Object.keys(filters).forEach((key) => {
  Vue.filter(key, filters[key])
})
// global instance method
Vue.prototype.has = function has(permission) {
  const splited = permission.split(',')
  const method = splited[0]
  // Remove the query parameters from the url
  const url = splited[1].split('?')[0]
  const { permissions } = store.state.base
  if (permissions[url] && permissions[url].includes(method)) {
    return true
  }
  return false
}

// map
VueAMap.initAMapApiLoader({
  key: 'c46bfd7e8adcee87b05cce249fed42a1',
  plugin: [
    'AMap.Autocomplete',
    'AMap.PlaceSearch',
    'AMap.Scale',
    'AMap.OverView',
    'AMap.ToolBar',
    'AMap.MapType',
    'AMap.PolyEditor',
    'AMap.CircleEditor',
    'AMap.Geocoder',
    'AMap.MouseTool',
    'AMap.PolyEditor',
    'AMap.CircleEditor',
  ],
  uiVersion: '1.0',
  v: '1.4.4',
})

lazyAMapApiLoaderInstance.load().then(() => {
})

// language
const i18n = new VueI18n({
  locale: window.localStorage.getItem('language') === 'en' ? 'en' : 'zh',
  messages: lang,
})
ElementLocale.i18n((key, value) => i18n.t(key, value))

sync(store, router)

window.onload = () => {
  setTimeout(() => {
    document.documentElement.scrollTop = 0
  }, 0)
}

new Vue({
  router,
  store,
  i18n,
  ...App,
}).$mount('#root')
