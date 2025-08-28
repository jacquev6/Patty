<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

import IdentifiedUser from '@/IdentifiedUser.vue'
import WhiteSpace from '@/WhiteSpace.vue'
import { useAuthenticatedClient } from '@/apiClient'

const model = defineModel<string>({ required: true })

const { t } = useI18n()
const client = useAuthenticatedClient()

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
  <span class="user">({{ t('fixedBy') }} <IdentifiedUser />)</span>
</template>

<style scoped>
span.user {
  color: grey;
}
</style>

<i18n>
en:
  fixedBy: fixed by
fr:
  fixedBy: corrigé par
</i18n>
