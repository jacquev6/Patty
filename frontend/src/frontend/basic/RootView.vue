<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import AuthenticationModal from './AuthenticationModal.vue'
import FrontendRootViewAuthenticated from './RootViewAuthenticated.vue'

const { t } = useI18n()
const { d } = useI18n({ useScope: 'global' })

const authenticationTokenStore = useAuthenticationTokenStore()

function validDate(date: string): Date | null {
  const d = new Date(date)
  if (isNaN(d.getFullYear())) {
    return null
  } else {
    return d
  }
}

const fromSubstitution = validDate('##TO_BE_SUBSTITUTED_UNAVAILABLE_UNTIL##')

const fromQuery = (() => {
  // Only for dev. Format: 2025-12-31T23:59:59.999Z
  const q = new URLSearchParams(window.location.search).get('unavailableUntil')
  if (q === null) {
    return null
  } else {
    return validDate(q)
  }
})()

const forceAvailable = (() => {
  // For testing during maintenance.
  const q = new URLSearchParams(window.location.search).get('forceAvailable')
  if (q === null) {
    return false
  } else {
    return q === 'true'
  }
})()

const unavailableUntil = forceAvailable ? null : (fromSubstitution ?? fromQuery)
</script>

<template>
  <template v-if="unavailableUntil !== null">
    <h1>{{ t('unavailable') }}</h1>
    <p>{{ t('inProgress', { datetime: d(unavailableUntil, 'long') }) }}</p>
  </template>
  <template v-else-if="authenticationTokenStore.token === null">
    <AuthenticationModal />
  </template>
  <FrontendRootViewAuthenticated v-else />
</template>

<i18n>
en:
  unavailable: "Unavailable"
  inProgress: "A maintenance operation is in in progress. Malin should be available again on {datetime}."
fr:
  unavailable: "Indisponible"
  inProgress: "Une opération de maintenance est en cours. Malin devrait être de nouveau disponible le {datetime}."
</i18n>
