import type { Theme } from '@vuepress/core'
import { defaultTheme } from '@vuepress/theme-default'
import type { DefaultThemeOptions } from '@vuepress/theme-default'
import { path } from '@vuepress/utils'

interface LocalThemeOptions extends DefaultThemeOptions {
  title?: string
  description?: string
}

export const localTheme = (options: LocalThemeOptions): Theme => {
  return {
    name: 'vuepress-theme-local',
    extends: defaultTheme(options),
    layouts: {
      Layout: path.resolve(__dirname, './Layout.vue'),
    },
  } as Theme
}
