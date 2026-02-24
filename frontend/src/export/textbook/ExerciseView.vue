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

import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import assert from '$/assert'
import type { Data } from './RootView.vue'
import { useDisplayPreferences } from './displayPreferences'

const props = defineProps<{
  id: string
  data: Data
}>()

const exercise = computed(() => {
  const exercise = props.data.exercises.find(
    (exercise) => exercise.kind === 'adapted' && exercise.exerciseId === props.id,
  )
  if (!exercise) {
    throw new Error('Exercise not found')
  }
  assert(exercise.kind === 'adapted')
  return exercise
})

const { tricolored } = useDisplayPreferences()
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" :tricolored />
</template>
