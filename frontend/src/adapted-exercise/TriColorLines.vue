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

<script lang="ts">
/* Colors provided by client */
export const colors: [string, string, string] = ['rgb(0, 0, 255)', 'rgb(255, 0, 0)', 'rgb(0, 204, 0)']
</script>

<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import { nextTick, onMounted, onUpdated, provide, ref, useTemplateRef, watch } from 'vue'
import _ from 'lodash'

import assert from '$/assert'

const props = defineProps<{
  tricolored: boolean
}>()

const container = useTemplateRef('container')
const { width } = useElementSize(container)
watch(width, () => nextTick(recolor))
onMounted(recolor)
onUpdated(recolor)

// Client found a situation where the colors were not updated. I have no idea why :-/
// (https://github.com/jacquev6/Gabby/issues/76)
// So, better safe than sorry, let's update the colors periodically.
setInterval(recolor, 1000)

const tricolorablesTriggerRecoloring = ref(0)
provide('tricolorablesTriggerRecoloring', tricolorablesTriggerRecoloring)

watch(tricolorablesTriggerRecoloring, () => nextTick(recolor))

const tricolorablesRevisionIndex = ref(0)
provide('tricolorablesRevisionIndex', tricolorablesRevisionIndex)

function recolor() {
  if (container.value !== null) {
    let somethingChanged = false

    const tricolorables = Array.from(
      container.value.getElementsByClassName('tricolorable') as HTMLCollectionOf<HTMLElement>,
    )

    if (props.tricolored) {
      type Line = { top: number; bottom: number; tricolorables: HTMLElement[] }
      const lines: Line[] = []
      const nonBaselineElements: HTMLElement[] = []
      tricolorables.forEach((element) => {
        if (isIndexOrExponent(element)) {
          nonBaselineElements.push(element)
        } else {
          const { top, bottom } = element.getBoundingClientRect()
          const line = lines.find(
            (line) =>
              (line.top <= top && line.bottom >= bottom) || // Element fully inside line's height
              (line.top >= top && line.bottom <= bottom), // or line fully inside element's height
          )
          if (line) {
            line.top = Math.min(line.top, top)
            line.bottom = Math.max(line.bottom, bottom)
            line.tricolorables.push(element)
          } else {
            lines.push({ top, bottom, tricolorables: [element] })
          }
        }
      })
      // `lines` is empty if there is no baseline-aligned tricolorable.
      // We do not handle this pathological case, and keep the text black.
      if (lines.length !== 0) {
        nonBaselineElements.forEach((element) => {
          const { top, bottom } = element.getBoundingClientRect()
          const line = _.maxBy(
            lines,
            // Portion of element's height overlapping with line
            (line) => Math.min(bottom, line.bottom) - Math.max(top, line.top),
          )
          assert(line !== undefined)
          line.tricolorables.push(element)
        })

        lines.sort((a, b) => a.top - b.top)

        lines.forEach((line, i) => {
          const color = colors[i % colors.length]
          line.tricolorables.forEach((element) => {
            if (element.style.color !== color) {
              somethingChanged = true
              element.style.color = color
            }
          })
        })
      }
    } else {
      tricolorables.forEach((element) => {
        if (element.style.color !== '') {
          somethingChanged = true
          element.style.color = ''
        }
      })
    }

    if (somethingChanged) {
      tricolorablesRevisionIndex.value += 1
    }
  }
}

function isIndexOrExponent(element: HTMLElement): boolean {
  assert(container.value !== null)

  while (element !== container.value) {
    const verticalAlign = getComputedStyle(element)['verticalAlign']
    if (verticalAlign === 'sub' || verticalAlign === 'super') {
      return true
    } else {
      assert(element.parentElement !== null)
      element = element.parentElement
    }
  }
  return false
}

defineExpose({ recolor })
</script>

<template>
  <div ref="container"><slot></slot></div>
</template>

<style scoped>
:deep(.tricolorable .tricolorable) {
  background-color: red;
}

:deep(.tricolorable .tricolorable::after) {
  content: 'BUG (nested tricolorable)';
  color: white;
}
</style>
