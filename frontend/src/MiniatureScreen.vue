<script setup lang="ts">
import { useElementBounding, useWindowSize } from '@vueuse/core'
import { computed, useTemplateRef, type StyleValue } from 'vue'

const props = defineProps<{
  fullScreen: boolean
}>()

const { width: windowWidth, height: windowHeight } = useWindowSize()
const aspectRatio = computed(() => windowWidth.value / windowHeight.value)

const { width: outerContainerWidth } = useElementBounding(useTemplateRef('outerContainer'))

const scale = computed(() => outerContainerWidth.value / windowWidth.value)

const outerContainerStyle = computed<StyleValue>(() => {
  const height = Math.ceil(windowHeight.value * scale.value)
  return {
    height: `${height}px`,
  }
})

const innerContainerStyle = computed<StyleValue>(() => {
  if (props.fullScreen) {
    return {
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
    }
  } else {
    return {
      aspectRatio: aspectRatio.value,
      width: `${windowWidth.value}px`,
      transform: `translate(-50%, -50%) scale(${scale.value}) translate(50%, 50%)`,
    }
  }
})
</script>

<template>
  <div class="bordered">
    <div ref="outerContainer" :style="outerContainerStyle">
      <div class="inner-container" :style="innerContainerStyle">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bordered {
  border: 1px solid black;
}

.inner-container {
  background-color: white;
  overflow: hidden;
}
</style>
