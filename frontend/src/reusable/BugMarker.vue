<script setup lang="ts">
defineProps<{
  is: string
  m: string
  v: never
}>()
</script>

<template>
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <component :is class="bug">BUG ({{ m }}): {{ v }}</component>
</template>

<style scoped>
.bug {
  color: red;
  font-weight: bold;
}
</style>
