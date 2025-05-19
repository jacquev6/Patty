<script setup lang="ts">
function click() {
  const el = document.activeElement
  if (el instanceof HTMLElement && el.getAttribute('contenteditable') !== null) {
    el.innerText = ''
    el.dispatchEvent(new InputEvent('input', { inputType: '' }))
  } else {
    console.log('Active element not handled:', el)
  }
}
</script>

<template>
  <button @pointerdown.prevent="click"><span class="eraser"></span></button>
</template>

<style scoped>
.eraser {
  display: inline-block;
  width: 1.5em;
  height: 0.7em;
  background: linear-gradient(to right, #ff7e89 0% 50%, #71b2f3 50% 100%);
  /* Thank you Chat GPT for the CSS magic */
  clip-path: polygon(10% 0%, 100% 0%, 90% 100%, 0% 100%);
  transform: rotate(-15deg);
}
</style>
