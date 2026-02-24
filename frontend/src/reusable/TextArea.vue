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
import { computed, nextTick, onMounted, useTemplateRef, watch } from 'vue'
import autosize from 'autosize'

import assert from '$/assert'

const model = defineModel<string>({ required: true })

const textareaRef = useTemplateRef('textarea')

onMounted(() => {
  assert(textareaRef.value !== null)
  autosize(textareaRef.value)
})

watch(model, async () => {
  assert(textareaRef.value !== null)
  await nextTick()
  autosize.update(textareaRef.value)
})

defineExpose({
  wrapped: computed(() => {
    assert(textareaRef.value !== null)
    return textareaRef.value
  }),
})
</script>

<template>
  <textarea ref="textarea" v-model="model"></textarea>
</template>

<style scoped>
textarea {
  width: 100%;
  resize: none;
}
</style>
