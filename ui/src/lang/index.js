import enLocale from 'element-ui/lib/locale/lang/en'
import zhLocale from 'element-ui/lib/locale/lang/zh-CN'

import commonEnLang from '@/lang/en'
import commonZhLang from '@/lang/zh_CN'
import { layoutEnLang, layoutZhLang } from '@/layout/lang'
import { appsEnLang, appsZhLang } from '@/apps/lang'

export default {
  en: { ...enLocale, ...commonEnLang, ...appsEnLang, ...layoutEnLang },
  zh: { ...zhLocale, ...commonZhLang, ...appsZhLang, ...layoutZhLang },
}
