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

import type { AnyRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import AnySequenceComponent from '@/adapted-exercise/dispatch/AnySequenceComponent.vue'

const props = defineProps<{
  contents: AnyRenderable[]
  bold: boolean
  italic: boolean
  underlined: boolean
  highlighted: string | null
  boxed: boolean
  subscript: boolean
  superscript: boolean
  tricolorable: boolean
}>()

const style = computed(() => ({
  backgroundColor: props.highlighted ?? undefined,
  fontWeight: props.bold ? 'bold' : undefined,
  fontStyle: props.italic ? 'italic' : undefined,
  border: props.boxed ? '2px solid black' : undefined,
  padding: props.boxed ? '4px' : undefined,
  textDecorationLine: props.underlined ? 'underline' : undefined,
  verticalAlign: props.subscript ? 'sub' : props.superscript ? 'super' : undefined,
  fontSize: props.subscript || props.superscript ? '0.8em' : undefined,
}))
</script>

<template>
  <span :style><AnySequenceComponent :contents :tricolorable /></span>
</template>
