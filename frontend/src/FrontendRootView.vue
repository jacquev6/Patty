<script setup lang="ts">
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import AuthenticationModal from './AuthenticationModal.vue'
import FrontendRootViewAuthenticated from './FrontendRootViewAuthenticated.vue'

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
    <h1>Unavailable</h1>
    <p>Patty is undergoing a maintenance operation. It's expected to be back on {{ unavailableUntil }}.</p>
  </template>
  <template v-else-if="authenticationTokenStore.token === null">
    <AuthenticationModal />
  </template>
  <FrontendRootViewAuthenticated v-else />
</template>
