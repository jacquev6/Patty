// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
