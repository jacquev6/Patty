<!--
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n({ useScope: 'global' })
const { t } = useI18n()
</script>
-->

<template>
  <form autocomplete="off">
    <!--
    <label>
      🌐
      <select v-model="locale">
        <option v-for="l in availableLocales" :key="l" :value="l">{{ t('language', 0, { locale: l }) }}</option>
      </select>
    </label>
    -->
  </form>
</template>

<!--
<i18n>
en:
  language: "🇺🇸 English"
fr:
  language: "🇫🇷 Français"
</i18n>
-->
