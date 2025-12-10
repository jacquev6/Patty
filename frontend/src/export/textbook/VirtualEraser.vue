<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import VirtualKeyboardButton from './VirtualKeyboardButton.vue'

function click() {
  const el = document.activeElement
  if (el instanceof HTMLElement && el.getAttribute('contenteditable') !== null) {
    el.textContent = ''
    el.dispatchEvent(new InputEvent('input', { inputType: '' }))
  } else {
    console.log('Active element not handled:', el)
  }
}
</script>

<template>
  <!-- VirtualEraser.png has been provided by the client in https://github.com/jacquev6/Patty/issues/91 -->
  <VirtualKeyboardButton @click="click"><img height="32" src="./VirtualEraser.png" /></VirtualKeyboardButton>
</template>

<style scoped>
img {
  vertical-align: text-bottom;
}
</style>
