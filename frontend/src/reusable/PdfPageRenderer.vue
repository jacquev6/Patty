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
import { useElementSize, watchDebounced } from '@vueuse/core'

import pdfjs, { type PDFPageProxy, type RenderTask } from './pdfjs'
import BusyBox from './BusyBox.vue'
import assert from './assert'
import { computed, onMounted, ref, useTemplateRef, watch } from 'vue'

const props = defineProps<{
  page: PDFPageProxy
}>()

const container = useTemplateRef('container')
const containerSize = useElementSize(container, { width: 0, height: 0 })
const containerWidth = computed(() => Math.round(containerSize.width.value) - 3)
const canvas = useTemplateRef('canvas')

const width = ref(210)
const height = ref(297)

const renderedPage = ref<number | null>(null)

let renderTask: RenderTask | null = null
const busy = ref(false)
async function draw() {
  if (canvas.value !== null && containerWidth.value > 0) {
    const startTime = performance.now()

    busy.value = true
    let resetOnExit = true

    try {
      const viewport = (() => {
        const viewport = props.page.getViewport({ scale: 1 })
        const scale = containerWidth.value / viewport.width
        return props.page.getViewport({ scale })
      })()
      height.value = Math.round(viewport.height)
      width.value = Math.round(viewport.width)

      renderTask?.cancel()
      const canvasContext = canvas.value.getContext('2d')
      assert(canvasContext !== null)
      renderTask = props.page.render({ canvasContext, viewport })
      try {
        await renderTask.promise
      } catch (e) {
        if (e instanceof pdfjs.RenderingCancelledException) {
          console.warn(
            `Was interrupted rendering page ${props.page.pageNumber} after ${Math.round(performance.now() - startTime)}ms`,
          )
          resetOnExit = false
          return
        } else {
          console.error(`Failed to render page ${props.page.pageNumber}`)
          throw e
        }
      }
      renderedPage.value = props.page.pageNumber
      console.info(
        `Rendered page ${props.page.pageNumber} at ${width.value}x${height.value} in ${Math.round(performance.now() - startTime)}ms`,
      )
    } finally {
      if (resetOnExit) {
        renderTask = null
        busy.value = false
      }
    }
  }
}

onMounted(async () => {
  await draw()
  watch(() => props.page, draw)
  watchDebounced(containerWidth, draw, { debounce: 250 })
})
</script>

<template>
  <BusyBox :busy>
    <div ref="container">
      <canvas ref="canvas" :width :height :data-cy-rendered-page="renderedPage"></canvas>
    </div>
  </BusyBox>
</template>

<style scoped>
canvas {
  border: 1px solid black;
}
</style>
