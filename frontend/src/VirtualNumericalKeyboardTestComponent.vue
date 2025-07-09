<script setup lang="ts">
import { ref } from 'vue'
import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import TriColoredInput from './TriColoredInput.vue'

const model = ref('')
</script>

<template>
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <p>
    TriColoredInput: <TriColoredInput :digitsOnly="true" v-model="model" /> <span>{{ model }}</span>
  </p>
  <p><VirtualNumericalKeyboard /></p>
</template>
