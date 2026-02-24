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
