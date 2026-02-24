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
