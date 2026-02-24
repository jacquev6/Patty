<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  pagesCount: number | null
}>()

const pageNumber = defineModel<number>({ required: true })

const emit = defineEmits<{
  (e: 'commit'): void
}>()

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

async function decrement() {
  --pageNumber.value
  emit('commit')
}

async function increment() {
  ++pageNumber.value
  emit('commit')
}
</script>

<template>
  <span>
    <button sm primary :disabled="pageNumber <= 1" @click="decrement">&lt;</button>
    <label>
      <input
        type="number"
        min="1"
        :max="pagesCount === null ? undefined : pagesCount"
        size="4"
        v-model="pageNumberProxy"
        @blur="emit('commit')"
      />
    </label>
    <button sm primary :disabled="pagesCount !== null && pageNumber >= pagesCount" @click="increment">&gt;</button>
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
