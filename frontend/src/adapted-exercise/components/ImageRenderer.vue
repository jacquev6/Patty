<script setup lang="ts">
defineProps<{
  url: string
}>()
</script>

<template>
  <img :src="url" />
</template>

<style scoped>
img {
  vertical-align: middle;
  margin: 0.5em;
}
</style>
