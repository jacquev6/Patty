<script setup lang="ts">
defineProps<{
  text: string
  tricolorable: boolean
}>()
</script>

<template>
  <span :class="{ tricolorable }">{{ text }}</span>
</template>
