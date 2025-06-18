<script setup lang="ts">
import { computed, inject, ref, useTemplateRef, watch } from 'vue'
import { useFloating, shift, flip, autoUpdate } from '@floating-ui/vue'

import type { FormattedText } from '@/apiClient'
import PassiveSequenceComponent from '../dispatch/PassiveSequenceComponent.vue'
import WhitespaceComponent from './WhitespaceComponent.vue'

defineOptions({
  inheritAttrs: false,
})

type FormattedTextContainer = {
  contents: FormattedText[]
}

const props = defineProps<{
  kind: 'multipleChoicesInput'
  choices: FormattedTextContainer[]
  showChoicesByDefault: boolean
  tricolorable: boolean
}>()

const model = defineModel<number | null>({ required: true })

const currentChoice = computed(() => {
  if (model.value === null) {
    return {
      contents: [{ kind: 'text' as const, text: '....' }],
    }
  } else {
    return props.choices[model.value]
  }
})

const floatingReference = useTemplateRef<HTMLElement>('floatingReference')
const floatingElement = useTemplateRef<HTMLDivElement>('floatingElement')
const { floatingStyles } = useFloating(floatingReference, floatingElement, {
  placement: 'bottom',
  middleware: [flip(), shift({ crossAxis: true })],
  whileElementsMounted: autoUpdate,
})

const showBackdrop = computed(() => !props.showChoicesByDefault)
const showChoices = ref(false)
watch(
  [() => props.showChoicesByDefault, model],
  ([showChoicesByDefault, model]) => {
    if (model === null) {
      showChoices.value = showChoicesByDefault
    } else {
      showChoices.value = false
    }
  },
  { immediate: true },
)

function set(choice: number) {
  model.value = choice
  showChoices.value = false
}

const choicesLines = computed(() => {
  const lines: { index: number; colorIndex: number; content: FormattedTextContainer }[][] = [[], []]
  for (let i = 0; i < props.choices.length; ++i) {
    lines[i % 2].push({ index: i, colorIndex: i % 3, content: props.choices[i] })
  }
  return lines
})

const teleportBackdropTo = inject<string /* or anything that can be passed to 'Teleport:to' */>(
  'adaptedExerciseTeleportBackdropTo',
  'body',
)
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
      <p><span class="choice">Alpha</span></p>
      <p><span class="choice">Bravo</span></p>
    </div>
  </div>
  <Teleport v-if="showChoices && teleportBackdropTo !== null" :to="teleportBackdropTo">
    <div data-cy="backdrop" v-if="showBackdrop" class="backdrop" @click="showChoices = false"></div>
    <div ref="floatingElement" :style="floatingStyles" class="choices">
      <p v-for="choicesLine in choicesLines">
        <template v-for="(choice, choiceIndex) in choicesLine">
          <WhitespaceComponent v-if="choiceIndex !== 0" kind="whitespace" />
          <span
            :data-cy="`choice${choice.index}`"
            @click="set(choice.index)"
            :class="`color-${choice.colorIndex}`"
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
  padding: 5px 10px;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
}

.choices p {
  margin-top: 34px;
  margin-bottom: 0;
}

.choices p:first-child {
  margin-top: 16px;
}

.choices p:last-child {
  margin-bottom: 16px;
}

.choice {
  cursor: pointer;
  border: 1px solid black;
  padding: 1px 4px;
}

/* Colors provided by client */
.color-0 {
  color: #00f;
}

.color-1 {
  color: #f00;
}

.color-2 {
  color: #0c0;
}
</style>
