<script setup lang="ts">
import { marked } from 'marked'
import { computed } from 'vue'

const props = defineProps<{
  markdown: string
}>()

const rendered = computed(() => marked(props.markdown))
</script>

<template>
  <div v-html="rendered"></div>
</template>

<style scoped>
:deep(pre),
:deep(code) {
  background-color: lightgrey;
}
</style>
