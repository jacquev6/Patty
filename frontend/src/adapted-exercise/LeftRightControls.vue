<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useMagicKeys } from '@vueuse/core'
import { watch } from 'vue'

const props = defineProps<{
  navigateUsingArrowKeys: boolean
  leftDisabled: boolean
  rightDisabled: boolean
}>()

const emit = defineEmits<{
  (e: 'goLeft'): void
  (e: 'goRight'): void
}>()

const { ArrowLeft, ArrowRight } = useMagicKeys()

function maybeGoLeft() {
  if (!props.leftDisabled) {
    emit('goLeft')
  }
}

function maybeGoRight() {
  if (!props.rightDisabled) {
    emit('goRight')
  }
}

watch(ArrowLeft, (value) => {
  if (props.navigateUsingArrowKeys && value) {
    maybeGoLeft()
  }
})

watch(ArrowRight, (value) => {
  if (props.navigateUsingArrowKeys && value) {
    maybeGoRight()
  }
})
</script>

<template>
  <div class="root">
    <div class="control" :class="{ disabled: leftDisabled }" @click="maybeGoLeft">
      <div class="arrow arrowLeft"></div>
    </div>
    <slot></slot>
    <div class="control" :class="{ disabled: rightDisabled }" @click="maybeGoRight">
      <div class="arrow"></div>
    </div>
  </div>
</template>

<style scoped>
.root {
  height: 100%;
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
  /* Arrow character copy-pasted from https://fsymbols.com/signs/arrow/ */
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
