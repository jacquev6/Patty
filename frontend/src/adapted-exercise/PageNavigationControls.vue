<script setup lang="ts">
import { computed } from 'vue'

import LeftRightControls from './LeftRightControls.vue'
import assert from '$/assert'

const props = defineProps<{
  navigateUsingArrowKeys: boolean
  pagesCount: number
}>()

assert(props.pagesCount > 0)

const model = defineModel<number>({ required: true })

const leftDisabled = computed(() => model.value === 0)
const rightDisabled = computed(() => model.value === props.pagesCount - 1)

function goLeft() {
  model.value -= 1
}

function goRight() {
  model.value += 1
}
</script>

<template>
  <LeftRightControls :navigateUsingArrowKeys :leftDisabled :rightDisabled @goLeft="goLeft" @goRight="goRight">
    <slot></slot>
  </LeftRightControls>
</template>
