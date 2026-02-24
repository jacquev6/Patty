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

import { computed } from 'vue'
import { defineStore } from 'pinia'
import { useStorage, StorageSerializers } from '@vueuse/core'

type TokenContainer = {
  token: string
  validUntil: string
}

export const useAuthenticationTokenStore = defineStore('authentication-token', () => {
  const tokenContainer = useStorage<TokenContainer | null>('patty/authentication-token/v1', null, undefined, {
    serializer: StorageSerializers.object,
  })

  function setExpirationTimeout() {
    if (tokenContainer.value !== null) {
      const validUntil = tokenContainer.value.validUntil
      const validUntilDate = new Date(validUntil)
      if (validUntilDate < new Date()) {
        tokenContainer.value = null
      } else {
        const remainingTime = validUntilDate.getTime() - Date.now()
        setTimeout(() => {
          if (tokenContainer.value !== null && tokenContainer.value.validUntil === validUntil) {
            tokenContainer.value = null
          }
        }, remainingTime)
        console.log(`Authentication token will expire in ${remainingTime}ms`)
      }
    }
    if (tokenContainer.value === null) {
      console.log('Authentication token is null')
    }
  }

  setExpirationTimeout()

  function set(token: string, validUntil: Date) {
    tokenContainer.value = { token, validUntil: validUntil.toISOString() }
    setExpirationTimeout()
  }

  const token = computed(() => {
    if (tokenContainer.value === null) {
      return null
    } else {
      return tokenContainer.value.token
    }
  })

  return { set, token }
})
