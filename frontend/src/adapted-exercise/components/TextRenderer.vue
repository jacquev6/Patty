<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
defineProps<{
  text: string
  tricolorable: boolean
}>()
</script>

<template>
  <span :class="{ tricolorable }">{{ text }}</span>
</template>
