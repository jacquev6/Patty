<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

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
      zIndex: 1,
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
  overflow: hidden;
}

.inner-container {
  background-color: white;
  overflow: hidden;
}
</style>
