/* eslint-disable */
import { expect } from 'chai'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import VueRouter from 'vue-router'
import TabsCardHead from '@/components/TabsCardHead'

const localVue = createLocalVue()
localVue.use(VueRouter)
const router = new VueRouter()

describe('TabsCardHead.vue', () => {
  const wrapper = shallowMount(TabsCardHead, {
    router,
    mocks: {
      $route: {
        path: '/',
      },
      $t: () => { }
    },
    propsData: {
      tabs: [
        { code: 'test1', url: '/' },
        { code: 'test2', url: '/test2' },
        { code: 'test3', url: '/test3' }
      ]
    }
  })
  it('能正确渲染 tab 的数量', () => {
    expect(wrapper.findAll('.crud-title').length).to.equal(3)
  })
  it('能正确显示 tab 的高亮', () => {
    // $route.path: '/' === tabs.url: '/'
    expect(wrapper.findAll('.crud-title').at(0).classes()).contains('active')
  })
})
