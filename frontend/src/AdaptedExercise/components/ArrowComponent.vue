<script setup lang="ts">
defineProps<{
  kind: 'arrow'
  tricolorable: boolean
}>()
</script>

<template>
  <span data-cy="arrow" :class="{ tricolorable }">→</span>
</template>
