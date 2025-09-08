<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient } from '@/frontend/ApiClient'
import WhiteSpace from '@/reusable/WhiteSpace.vue'

const model = defineModel<string>({ required: true })

const emit = defineEmits<{
  (e: 'done'): void
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()

const classNames = reactive<string[]>([])

onMounted(async () => {
  const response = await client.GET('/api/exercise-classes')
  if (response.data !== undefined) {
    classNames.splice(0, classNames.length, ...response.data)
  }
})
</script>

<template>
  <select data-cy="exercise-class" v-model="model">
    <option v-for="name in classNames">{{ name }}</option>
  </select>
  <WhiteSpace />
  <button @click="emit('done')">{{ t('ok') }}</button>
</template>

<style scoped>
span.user {
  color: grey;
}
</style>

<i18n>
en:
  ok: OK
fr:
  ok: OK
</i18n>
