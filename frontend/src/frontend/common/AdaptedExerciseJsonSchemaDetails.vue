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
import jsonStringify from 'json-stringify-pretty-compact'
import { useI18n } from 'vue-i18n'

defineProps<{
  schema: object
}>()

const { t } = useI18n()
</script>

<template>
  <details>
    <summary>{{ t('summary') }}</summary>
    <pre>{{ jsonStringify(schema, { maxLength: 120 }) }}</pre>
  </details>
</template>

<i18n>
en:
  summary: Click here to show the JSON schema the LLM's response must respect.
fr:
  summary: Cliquez ici pour afficher le schéma JSON que la réponse du LLM doit respecter.
</i18n>
