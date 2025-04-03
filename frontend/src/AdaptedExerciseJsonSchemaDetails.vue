<script setup lang="ts">
import jsonStringify from 'json-stringify-pretty-compact'

import adaptedExerciseSchema from '../../backend/adapted-exercise-schema.json'
</script>

<template>
  <details>
    <summary>Click here to show the JSON schema for the LLM's response.</summary>
    <pre>{{ jsonStringify(adaptedExerciseSchema, { maxLength: 120 }) }}</pre>
  </details>
</template>
