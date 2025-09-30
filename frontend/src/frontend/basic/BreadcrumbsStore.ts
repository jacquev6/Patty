import { defineStore } from 'pinia'
import { reactive } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

export type Breadcrumb = {
  textKey: string
  textArgs?: Record<string, string | number>
  to?: RouteLocationRaw
}
export type Breadcrumbs = Breadcrumb[]

export const useBreadcrumbsStore = defineStore('breadcrumbs', () => {
  const breadcrumbs = reactive<Breadcrumbs>([])

  function set(bs: Breadcrumbs) {
    breadcrumbs.splice(0, breadcrumbs.length, ...bs)
  }

  return {
    breadcrumbs,
    set,
  }
})
