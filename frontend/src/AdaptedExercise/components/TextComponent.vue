<script setup lang="ts">
defineProps<{
  kind: 'text'
  text: string
  tricolorable: boolean
}>()
</script>

<template>
  <span :class="{ tricolorable }">{{ text }}</span>
</template>
