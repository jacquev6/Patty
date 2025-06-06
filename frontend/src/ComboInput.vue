<!--
Rationale: why not use an <input type="text" list="id" /> with a <datalist>?

It behaves inconsistently across browsers:

- visual clue that there is a suggestion list:
  - Chrome: an arrow is displayed when the mouse is over the input or the input is focused
  - Firefox: no visual clue
- suggestions list is not shown in the same circumstances:
  - Chrome: when the input is clicked once (but not just focused) or typed in and contains at least 1 character
  - Firefox: when the input is focused *then* clicked or typed in and contains at least 1 character

To homogenize that, we could use the following:

- HTMLInputElement.showPicker but it's not widely supported for input with datalist
(https://caniuse.com/mdn-api_htmlinputelement_showpicker_datalist_input)
- onmouseover="focus();" but this has too many side effects
(https://stackoverflow.com/a/77045720/905845)

So, on behalf of my client I want:

- a permanent visual clue that the input has a suggestion list
- the suggestion list to be shown as soon and as long as the input has focus (even if current value is empty)

And I have to provide an ad-hoc implementation.
-->

<script setup lang="ts">
import { useElementSize, useFocus } from '@vueuse/core'
import { computed, useTemplateRef } from 'vue'
import { useFloating } from '@floating-ui/vue'
import { levenshteinEditDistance } from 'levenshtein-edit-distance'

const props = defineProps<{
  suggestions: string[]
}>()

const model = defineModel<string>({ required: false, default: '' })

const inputElement = useTemplateRef('inputElement')
const suggestionsElement = useTemplateRef('suggestionsElement')

const { focused } = useFocus(inputElement)

const sortedSuggestions = computed(() => {
  const needle = model.value.toLowerCase()
  if (model.value === '') {
    return props.suggestions.map((suggestion) => ({ found: 0, index: -1, suggestion }))
  } else {
    return props.suggestions
      .map((suggestion) => ({ distance: levenshteinEditDistance(needle, suggestion.toLowerCase()), suggestion }))
      .sort((a, b) => a.distance - b.distance)
      .map(({ suggestion }) => {
        const index = suggestion.toLowerCase().indexOf(needle)
        const found = index !== -1 ? 1 : 0
        return { found, index, suggestion }
      })
      .sort((a, b) => b.found - a.found)
  }
})

const { floatingStyles } = useFloating(inputElement, suggestionsElement, { placement: 'bottom-start' })

const { width: inputElementWidth } = useElementSize(inputElement, { width: 100, height: 100 }, { box: 'border-box' })
const sizeStyles = computed(() => {
  return {
    width: `${inputElementWidth.value}px`,
  }
})

const style = computed(() => {
  return { ...sizeStyles.value, ...floatingStyles.value }
})
</script>

<template>
  <input ref="inputElement" v-model="model" type="text" v-bind="$attrs" />
  <span v-if="!focused" class="clue"></span>
  <Teleport to="body" v-if="focused">
    <div ref="suggestionsElement" class="suggestions" :style>
      <p
        data-cy="suggestion"
        v-for="{ index, suggestion } in sortedSuggestions"
        class="suggestion"
        @mousedown="model = suggestion"
      >
        <template v-if="index === -1">{{ suggestion }}</template>
        <template v-else>
          {{ suggestion.slice(0, index) }}<strong>{{ suggestion.slice(index, index + model.length) }}</strong
          >{{ suggestion.slice(index + model.length) }}
        </template>
      </p>
    </div>
  </Teleport>
</template>

<style scoped>
div.suggestions {
  background-color: white;
  border: 1px solid black;
}
div.suggestions > p {
  margin: 0;
  padding: 0;
}
div.suggestions > p.suggestion {
  cursor: pointer;
}
div.suggestions > p.suggestion:hover {
  background-color: #ccc;
}
span.clue {
  display: inline-block;
  height: 0.6em;
  margin-left: -15px;
  margin-right: 5px;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 8px solid black;
  cursor: text;
}
</style>
