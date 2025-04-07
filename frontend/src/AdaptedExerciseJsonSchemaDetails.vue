<script setup lang="ts">
import jsonStringify from 'json-stringify-pretty-compact'

defineProps<{
  schema: object
}>()
</script>

<template>
  <details>
    <summary>Click here to show the resulting JSON schema for the LLM's response.</summary>
    <pre>{{ jsonStringify(schema, { maxLength: 120 }) }}</pre>
  </details>
</template>
