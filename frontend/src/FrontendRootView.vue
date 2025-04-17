<script setup lang="ts">
import { RouterView } from 'vue-router'

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

const unavailableUntil = fromSubstitution ?? fromQuery
</script>

<template>
  <template v-if="unavailableUntil !== null">
    <h1>Unavailable</h1>
    <p>Patty is undergoing a maintenance operation. It's expected to be back on {{ unavailableUntil }}.</p>
  </template>
  <RouterView v-else />
</template>
