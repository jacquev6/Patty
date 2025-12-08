<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import jsonStringify from 'json-stringify-pretty-compact'
import { useI18n } from 'vue-i18n'

defineProps<{
  schema: object
}>()

const { t } = useI18n()
</script>

<template>
  <details>
    <summary>{{ t('summary') }}</summary>
    <pre>{{ jsonStringify(schema, { maxLength: 120 }) }}</pre>
  </details>
</template>

<i18n>
en:
  summary: Click here to show the JSON schema the LLM's response must respect.
fr:
  summary: Cliquez ici pour afficher le schéma JSON que la réponse du LLM doit respecter.
</i18n>
