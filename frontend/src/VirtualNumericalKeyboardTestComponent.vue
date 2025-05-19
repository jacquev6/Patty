<script setup lang="ts">
import { ref } from 'vue'
import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import TriColoredInput from './TriColoredInput.vue'

const model = ref('')
</script>

<template>
  <p>
    TriColoredInput: <TriColoredInput :digitsOnly="true" v-model="model" /> <span>{{ model }}</span>
  </p>
  <p><VirtualNumericalKeyboard /></p>
</template>
