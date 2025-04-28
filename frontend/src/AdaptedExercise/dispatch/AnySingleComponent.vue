<script setup lang="ts">
import { computed } from 'vue'

import type { AnyComponent } from '@/apiClient'
import assert from '@/assert'
import PassiveSingleComponent, { isPassive } from './PassiveSingleComponent.vue'
import FreeTextInput from '../components/FreeTextInput.vue'
import MultipleChoicesInput from '../components/MultipleChoicesInput.vue'
import SelectableInput from '../components/SelectableInput.vue'
import SwappableInput from '../components/SwappableInput.vue'
import type { StudentAnswers, ComponentAnswer, InProgressExercise } from '../AdaptedExerciseRenderer.vue'
import PassiveSequenceComponent from './PassiveSequenceComponent.vue'
import EditableTextInput from '../components/EditableTextInput.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  componentIndex: number
  component: AnyComponent
  tricolorable: boolean
}>()

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const inProgress = defineModel<InProgressExercise>('inProgress', { required: true })

function getComponentAnswer() {
  return studentAnswers.value.pages[props.pageIndex]?.lines[props.lineIndex]?.components[props.componentIndex]
}

function setComponentAnswer(answer: ComponentAnswer) {
  studentAnswers.value.pages[props.pageIndex] ??= { lines: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex] ??= { components: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex]!.components[props.componentIndex] = answer
}

const answerForFreeTextInput = computed<string>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return ''
    } else {
      assert(answer.kind === 'freeTextInput')
      return answer.text
    }
  },
  set: (text: string) => {
    setComponentAnswer({ kind: 'freeTextInput', text })
  },
})

const answerForMultipleChoicesInput = computed<number | null, number | null>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return null
    } else {
      assert(answer.kind === 'multipleChoicesInput')
      return answer.choice
    }
  },
  set: (choice: number | null) => {
    setComponentAnswer({ kind: 'multipleChoicesInput', choice })
  },
})

const answerForSelectableInput = computed<number, number>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return 0
    } else {
      assert(answer.kind === 'selectableInput')
      return answer.color
    }
  },
  set: (color: number) => {
    setComponentAnswer({ kind: 'selectableInput', color })
  },
})
</script>

<template>
  <PassiveSingleComponent v-if="isPassive(component)" :component="component" :tricolorable="tricolorable" />
  <FreeTextInput
    v-else-if="component.kind === 'freeTextInput'"
    v-bind="component"
    v-model="answerForFreeTextInput"
    :tricolorable
  />
  <MultipleChoicesInput
    v-else-if="component.kind === 'multipleChoicesInput'"
    v-bind="component"
    v-model="answerForMultipleChoicesInput"
    :tricolorable
  />
  <SelectableInput
    v-else-if="component.kind === 'selectableInput'"
    v-bind="component"
    v-model="answerForSelectableInput"
    :tricolorable
  />
  <SwappableInput
    v-else-if="component.kind === 'swappableInput'"
    :pageIndex
    :lineIndex
    :componentIndex
    v-bind="component"
    v-model="studentAnswers"
    v-model:inProgress="inProgress"
    :tricolorable
  />
  <PassiveSequenceComponent
    v-else-if="component.kind === 'editableTextInput'"
    :contents="component.contents"
    :tricolorable
  />
  <EditableTextInput
    v-else-if="component.kind === 'activeEditableTextInput'"
    :pageIndex
    :lineIndex
    :componentIndex
    v-bind="component"
    v-model="studentAnswers"
    :tricolorable
  />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
