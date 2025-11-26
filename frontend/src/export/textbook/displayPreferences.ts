import { useStorage } from '@vueuse/core'
import { computed, inject, provide } from 'vue'

import assert from '$/assert'

export type StoredDisplayPreferences = {
  tricolored: boolean
}

const storageKey = 'patty/display-preferences/v1'
const injectKey = 'display-preferences'

function makeDisplayPreferences() {
  const prefs = useStorage<StoredDisplayPreferences>(storageKey, { tricolored: true })
  return {
    tricolored: computed({
      get: () => prefs.value.tricolored,
      set: (value: boolean) => {
        prefs.value.tricolored = value
      },
    }),
  }
}

export function provideDisplayPreferences() {
  provide(injectKey, makeDisplayPreferences())
}

export function useDisplayPreferences() {
  const displayPreferences = inject<ReturnType<typeof makeDisplayPreferences>>(injectKey)
  assert(displayPreferences !== undefined)
  return displayPreferences
}
