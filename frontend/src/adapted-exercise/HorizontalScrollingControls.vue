<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { useScroll } from '@vueuse/core'

import LeftRightControls from './LeftRightControls.vue'
import assert from '$/assert'

const props = defineProps<{
  navigateUsingArrowKeys: boolean
  scrollBy: number
}>()

const content = useTemplateRef('content')

const position = useScroll(content)

const leftDisabled = computed(() => {
  if (content.value === null) {
    return true
  } else {
    return position.x.value <= 0
  }
})
const rightDisabled = computed(() => {
  if (content.value === null) {
    return true
  } else {
    return position.x.value + content.value.clientWidth >= content.value.scrollWidth
  }
})

function goLeft() {
  assert(content.value !== null)
  content.value.scrollBy({ left: -props.scrollBy, behavior: 'smooth' })
}

function goRight() {
  assert(content.value !== null)
  content.value.scrollBy({ left: props.scrollBy, behavior: 'smooth' })
}
</script>

<template>
  <LeftRightControls :navigateUsingArrowKeys :leftDisabled :rightDisabled @goLeft="goLeft" @goRight="goRight">
    <div ref="content" class="content">
      <slot></slot>
    </div>
  </LeftRightControls>
</template>

<style scoped>
div.content {
  overflow-x: scroll;
}
</style>
