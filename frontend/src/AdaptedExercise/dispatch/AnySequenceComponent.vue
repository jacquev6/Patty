<script setup lang="ts">
import type { AnyComponent } from '@/apiClient'
import AnySingleComponent from './AnySingleComponent.vue'
import { type InProgressExercise, type StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  contents: AnyComponent[]
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
    :aloneOnLine="false"
    :componentIndex
    :component
    :tricolorable
    v-model="model"
    v-model:inProgress="inProgress"
  />
</template>
