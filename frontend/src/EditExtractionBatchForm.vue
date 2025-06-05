<script setup lang="ts">
import { type ExtractionBatch } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'

defineProps<{
  extractionBatch: ExtractionBatch
}>()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ extractionBatch.createdBy }}</p>
  <p>
    <a :href="`/api/export/extraction-batch/${extractionBatch.id}.html?token=${authenticationTokenStore.token}`">
      Download standalone HTML
    </a>
  </p>
</template>
