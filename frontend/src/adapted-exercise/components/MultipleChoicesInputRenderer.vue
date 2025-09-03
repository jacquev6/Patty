<script setup lang="ts">
import { computed, inject, reactive, useTemplateRef, watch, type Ref } from 'vue'
import { useFloating, shift, flip, autoUpdate } from '@floating-ui/vue'

import type {
  InProgressExercise,
  PassiveRenderable,
  StudentAnswers,
} from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import PassiveSequenceComponent from '@/adapted-exercise/dispatch/PassiveSequenceComponent.vue'
import WhitespaceRenderer from './WhitespaceRenderer.vue'
import assert from '$/assert'
import { colors } from '@/adapted-exercise/TriColorLines.vue'

defineOptions({
  inheritAttrs: false,
})

type FormattedTextContainer = {
  contents: PassiveRenderable[]
}

const props = defineProps<{
  path: string
  choices: FormattedTextContainer[]
  showChoicesByDefault: boolean
  tricolorable: boolean
}>()

const studentAnswers = inject<Ref<StudentAnswers>>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const inProgress = inject<InProgressExercise>('adaptedExerciseInProgress')
assert(inProgress !== undefined)

const choiceProxy = computed({
  get() {
    const answer = studentAnswers.value[props.path]
    if (answer === undefined) {
      return undefined
    } else {
      assert(answer.kind === 'choice')
      return answer.choice
    }
  },
  set(choice: number | null) {
    studentAnswers.value[props.path] = { kind: 'choice', choice }
  },
})

const currentChoice = computed(() => {
  if (choiceProxy.value === null || choiceProxy.value === undefined) {
    return {
      contents: [{ kind: 'text' as const, text: '....' }],
    }
  } else {
    return props.choices[choiceProxy.value]
  }
})

const floatingReference = useTemplateRef('floatingReference')
const floatingElement = useTemplateRef('floatingElement')
const { floatingStyles } = useFloating(floatingReference, floatingElement, {
  placement: 'bottom',
  middleware: [flip(), shift({ crossAxis: true })],
  whileElementsMounted: autoUpdate,
})

const showBackdrop = computed(() => !props.showChoicesByDefault)
const showChoices = computed({
  get() {
    return (
      (choiceProxy.value === undefined && props.showChoicesByDefault) ||
      (inProgress.p.kind === 'solvingMultipleChoices' && inProgress.p.path === props.path)
    )
  },
  set(value: boolean) {
    if (value) {
      inProgress.p = {
        kind: 'solvingMultipleChoices',
        path: props.path,
      }
    } else {
      inProgress.p = { kind: 'none' }
      if (choiceProxy.value === undefined) {
        choiceProxy.value = null
      }
    }
  },
})

function set(choice: number) {
  choiceProxy.value = choice
  showChoices.value = false
}

const choicesLines = computed(() => {
  const lines: { index: number; colorIndex: number; content: FormattedTextContainer }[][] = [[], []]
  for (let i = 0; i < props.choices.length; ++i) {
    lines[i % 2].push({ index: i, colorIndex: i % 3, content: props.choices[i] })
  }
  return lines
})

const teleportBackdropTo = inject<Ref<HTMLDivElement> | null>('adaptedExerciseContainerDiv')
assert(teleportBackdropTo !== undefined)

const sortedColors = reactive([colors[0], colors[1], colors[2]])

const floatingElementStyle = computed(() => ({
  ...floatingStyles.value,
  '--color-0': sortedColors[0],
  '--color-1': sortedColors[1],
  '--color-2': sortedColors[2],
}))

const tricolorablesRevisionIndex = inject<Ref<number>>('tricolorablesRevisionIndex')
assert(tricolorablesRevisionIndex !== undefined)

function recolor() {
  if (floatingReference.value !== null) {
    const innerTricolorables = floatingReference.value.getElementsByClassName(
      'tricolorable',
    ) as HTMLCollectionOf<HTMLElement>
    if (innerTricolorables.length === 0) {
      sortedColors[0] = colors[0]
      sortedColors[1] = colors[1]
      sortedColors[2] = colors[2]
    } else {
      const index = colors.indexOf(innerTricolorables[0].style.color)
      if (index === -1) {
        sortedColors[0] = colors[0]
        sortedColors[1] = colors[1]
        sortedColors[2] = colors[2]
      } else {
        sortedColors[0] = colors[(index + 1) % colors.length]
        sortedColors[1] = colors[(index + 2) % colors.length]
        sortedColors[2] = colors[index]
      }
    }
  }
}

watch(tricolorablesRevisionIndex, recolor, { immediate: true })
</script>

<template>
  <div class="container">
    <p
      ref="floatingReference"
      data-cy="multipleChoicesInput"
      class="main"
      :class="{ showChoices }"
      @click="showChoices = !showChoices"
    >
      <PassiveSequenceComponent :contents="currentChoice.contents" :tricolorable />
    </p>
    <!-- Ensure the floating choices does not cover next line -->
    <div class="hidden choices">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <p><span class="choice">Alpha</span></p>
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <p><span class="choice">Bravo</span></p>
    </div>
  </div>
  <Teleport v-if="showChoices && teleportBackdropTo !== null" :to="teleportBackdropTo">
    <div data-cy="backdrop" v-if="showBackdrop" class="backdrop" @click="showChoices = false"></div>
    <div ref="floatingElement" :style="floatingElementStyle" class="choices">
      <p v-for="choicesLine in choicesLines">
        <template v-for="(choice, choiceIndex) in choicesLine">
          <WhitespaceRenderer v-if="choiceIndex !== 0" />
          <span
            :data-cy="`choice${choice.index}`"
            @click="set(choice.index)"
            :style="`color: var(--color-${choice.colorIndex})`"
            class="choice"
          >
            <PassiveSequenceComponent :contents="choice.content.contents" :tricolorable="false" />
          </span>
        </template>
      </p>
    </div>
  </Teleport>
</template>

<style scoped>
.container {
  display: inline flow-root;
  vertical-align: top;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
}

.main {
  cursor: pointer;
  display: inline;
  border: 2px outset #888;
}

.main.showChoices {
  background-color: #fffdd4;
}

.hidden {
  max-width: 0;
  visibility: hidden;
}

.backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.choices {
  border: 1px dashed green;
  background-color: white;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
  padding: 0 10px;
  line-height: var(--vertical-space-between-choices-lines);
}

.choices p:first-child {
  margin-top: calc(
    var(--vertical-space-between-border-and-choices) - (var(--vertical-space-between-choices-lines) - 1em) / 2
  );
}
.choices p:last-child {
  margin-bottom: calc(
    var(--vertical-space-between-border-and-choices) - (var(--vertical-space-between-choices-lines) - 1em) / 2
  );
}

.choice {
  cursor: pointer;
  border: 1px solid black;
  padding: 1px 4px;
}
</style>
