<script setup lang="ts">
import type { AnyRenderable } from '../AdaptedExerciseRenderer.vue'
import AnySingleComponent from './AnySingleComponent.vue'
import { type InProgressExercise, type StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  contents: AnyRenderable[]
  aloneOnLine: boolean
  tricolorable: boolean
}>()

const model = defineModel<StudentAnswers>({ required: true })

const inProgress = defineModel<InProgressExercise>('inProgress', { required: true })
</script>

<template>
  <AnySingleComponent
    v-for="(component, componentIndex) in props.contents"
    :pageIndex
    :lineIndex
    :aloneOnLine
    :componentIndex
    :component
    :tricolorable
    v-model="model"
    v-model:inProgress="inProgress"
  />
</template>
