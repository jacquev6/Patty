<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthenticatedClient } from './apiClient'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import BusyBox from './BusyBox.vue'
import InputForNonEmptyStringOrNull from './InputForNonEmptyStringOrNull.vue'
import InputForNumberOrNull from './InputForNumberOrNull.vue'

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const title = ref('')
const editor = ref<string | null>(null)
const year = ref<number | null>(null)
const isbn = ref<string | null>(null)

const disabled = computed(() => title.value === '')

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/textbooks', {
    body: {
      creator: identifiedUser.identifier,
      title: title.value,
      editor: editor.value,
      year: year.value,
      isbn: isbn.value,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'textbook', params: { id: response.data.id } })
  }
}
</script>

<template>
  <BusyBox :busy>
    <p>Created by: <IdentifiedUser /></p>
    <p>
      <label>Title: <input v-model="title" data-cy="textbook-title" /></label>
    </p>
    <p>
      <label>Editor: <InputForNonEmptyStringOrNull v-model="editor" data-cy="textbook-editor" /></label>
    </p>
    <p>
      <label>Year: <InputForNumberOrNull v-model="year" data-cy="textbook-year" /></label>
    </p>
    <p>
      <label>ISBN: <InputForNonEmptyStringOrNull v-model="isbn" data-cy="textbook-isbn" /></label>
    </p>
    <p><button @click="submit" :disabled>Submit</button></p>
  </BusyBox>
</template>
