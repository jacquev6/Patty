<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  pagesCount: number | null
}>()

const pageNumber = defineModel<number>('page', { default: 1 })

const pageNumberProxy = computed({
  get: () => pageNumber.value.toString(),
  set: (value_: string) => {
    const value = Number.parseInt(value_, 10)
    if (Number.isInteger(value)) {
      if (value < 1) {
        pageNumber.value = 1
      } else if (props.pagesCount !== null && value > props.pagesCount) {
        pageNumber.value = props.pagesCount
      } else {
        pageNumber.value = value
      }
    }
  },
})
</script>

<template>
  <span>
    <button sm primary :disabled="pageNumber <= 1" @click="--pageNumber">&lt;</button>
    <label>
      <input
        type="number"
        min="1"
        :max="pagesCount === null ? undefined : pagesCount"
        size="4"
        v-model.lazy="pageNumberProxy"
      />
    </label>
    <button sm primary :disabled="pagesCount !== null && pageNumber >= pagesCount" @click="++pageNumber">&gt;</button>
    <slot></slot>
  </span>
</template>

<style scoped>
/* https://www.w3schools.com/howto/howto_css_hide_arrow_number.asp */
input {
  -moz-appearance: textfield;
  appearance: textfield;
  width: 3em;
}
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
