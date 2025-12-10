// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

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
