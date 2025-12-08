// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

export const useIdentifiedUserStore = defineStore('identified-user', () => {
  return { identifier: useStorage('patty/identified-user/v1', '') }
})
