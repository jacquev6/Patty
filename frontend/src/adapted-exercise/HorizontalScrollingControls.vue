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
