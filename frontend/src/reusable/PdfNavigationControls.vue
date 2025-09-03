<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  pagesCount: number | null
}>()

const pageNumber = defineModel<number>('page', { default: 1 })
const requestedPageNumber = ref('')

function resetRequestedPageNumber() {
  requestedPageNumber.value = pageNumber.value.toString()
}

watch(pageNumber, resetRequestedPageNumber, { immediate: true })

watch(requestedPageNumber, () => {
  const page = Number.parseInt(requestedPageNumber.value, 10)
  if (Number.isInteger(page) && page >= 1 && (props.pagesCount === null || page <= props.pagesCount)) {
    pageNumber.value = page
  }
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
        v-model="requestedPageNumber"
        @blur="resetRequestedPageNumber"
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
