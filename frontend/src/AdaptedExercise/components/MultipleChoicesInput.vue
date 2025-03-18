<script setup lang="ts">
import { computed, inject, ref, useTemplateRef, watch } from 'vue'
import { useFloating, shift, flip, autoUpdate } from '@floating-ui/vue'

import type { Line } from '@/apiClient'
import LineComponent from './LineComponent.vue'
import WhitespaceComponent from './WhitespaceComponent.vue'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  kind: 'multipleChoicesInput'
  choices: Line[]
  showChoicesByDefault: boolean
}>()

const model = defineModel<number | null>({ default: null })

const currentChoice = computed(() => {
  if (model.value === null) {
    return {
      kind: 'sequence' as const,
      contents: [{ kind: 'text' as const, text: '....' }],
      bold: false,
      italic: false,
      highlighted: null,
      boxed: false,
      vertical: false,
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
  const lines: { index: number; colorIndex: number; content: Line }[][] = [[], []]
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
  <span ref="floatingReference" data-cy="multipleChoicesInput" @click="showChoices = !showChoices">
    <LineComponent :contents="currentChoice.contents" />
  </span>
  <Teleport v-if="showChoices && teleportBackdropTo !== null" :to="teleportBackdropTo">
    <div data-cy="backdrop" v-if="showBackdrop" class="backdrop" @click="showChoices = false"></div>
    <div ref="floatingElement" :style="floatingStyles">
      <p v-for="choicesLine in choicesLines">
        <template v-for="(choice, choiceIndex) in choicesLine">
          <WhitespaceComponent v-if="choiceIndex !== 0" kind="whitespace" />
          <span :data-cy="`choice${choice.index}`" @click="set(choice.index)">
            <LineComponent :contents="choice.content.contents" />
          </span>
        </template>
      </p>
    </div>
  </Teleport>
</template>

<style scoped>
div.backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
