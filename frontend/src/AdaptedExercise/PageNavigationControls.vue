<script setup lang="ts">
defineProps<{
  pagesCount: number
}>()

const model = defineModel<number>({ required: true })
</script>

<!-- Arrow characters copy-pasted from https://fsymbols.com/signs/arrow/ -->
<template>
  <div class="root">
    <div class="control" :class="{ disabled: model === 0 }" @click="model = Math.max(0, model - 1)">
      <div class="arrow arrowLeft"></div>
    </div>
    <div style="overflow-x: hidden"><slot></slot></div>
    <div
      class="control"
      :class="{ disabled: model === pagesCount - 1 }"
      @click="model = Math.min(pagesCount - 1, model + 1)"
    >
      <div class="arrow"></div>
    </div>
  </div>
</template>

<style scoped>
.root {
  --control-width: 35px;
  display: grid;
  grid-template-columns: var(--control-width) 1fr var(--control-width);
}

div.control {
  background: lightgrey;
  font-size: calc(0.9 * var(--control-width));
  line-height: 0;
  font-family: Arial, sans-serif;
  font-weight: 400;
  cursor: pointer;
  user-select: none;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

div.arrow {
  height: calc(2 * var(--control-width));
  width: 100%;
  background: grey;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: black;
  border-top-left-radius: var(--control-width);
  border-bottom-left-radius: var(--control-width);
}

div.arrow::before {
  content: '⮕';
  text-align: center;
}

div.arrowLeft {
  transform: scaleX(-1);
}

div.control.disabled {
  cursor: not-allowed;
}

div.control.disabled div.arrow {
  color: lightgrey;
}
</style>
