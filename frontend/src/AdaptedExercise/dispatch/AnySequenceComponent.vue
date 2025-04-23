<script setup lang="ts">
import type { AnyComponent } from '@/apiClient'
import AnySingleComponent from './AnySingleComponent.vue'
import type { StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  contents: AnyComponent[]
  tricolorable: boolean
}>()

const model = defineModel<StudentAnswers>({ required: true })
</script>

<template>
  <AnySingleComponent
    v-for="(component, componentIndex) in props.contents"
    :pageIndex
    :lineIndex
    :componentIndex
    :component
    :tricolorable
    v-model="model"
  />
</template>
