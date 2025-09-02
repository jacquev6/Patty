<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import BusyBox from '$/BusyBox.vue'
import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import InputForNumberOrNull from '$/InputForNumberOrNull.vue'

const router = useRouter()
const { t } = useI18n()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const title = ref('')
const publisher = ref<string | null>(null)
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
      publisher: publisher.value,
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
    <p>
      <label>{{ t('title') }} <input v-model="title" data-cy="textbook-title" /></label>
    </p>
    <p>
      <label
        >{{ t('publisher') }} <InputForNonEmptyStringOrNull v-model="publisher" data-cy="textbook-publisher"
      /></label>
    </p>
    <p>
      <label>{{ t('year') }} <InputForNumberOrNull v-model="year" data-cy="textbook-year" /></label>
    </p>
    <p>
      <label>{{ t('isbn') }} <InputForNonEmptyStringOrNull v-model="isbn" data-cy="textbook-isbn" /></label>
    </p>
    <p>
      <button @click="submit" :disabled>{{ t('submit') }}</button>
    </p>
  </BusyBox>
</template>

<i18n>
en:
  createdBy: Created by
  title: "Title:"
  publisher: "Publisher:"
  year: "Year:"
  isbn: "ISBN:"
  submit: Submit
fr:
  createdBy: "Créé par"
  title: "Titre :"
  publisher: "Éditeur :"
  year: "Année :"
  isbn: "ISBN :"
  submit: Soumettre
</i18n>
