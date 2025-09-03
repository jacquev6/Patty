<script setup lang="ts">
import { useStorage } from '@vueuse/core'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n({ useScope: 'global' })
const { t } = useI18n()

const savedLocale = useStorage('patty/user-selected-locale/v1', 'en')
watch(
  savedLocale,
  (newLocale) => {
    locale.value = newLocale
  },
  { immediate: true },
)
</script>

<template>
  <form autocomplete="off">
    <label>
      🌐
      <select data-cy="localeSelect" v-model="savedLocale">
        <option v-for="l in availableLocales" :key="l" :value="l">{{ t('language', 0, { locale: l }) }}</option>
      </select>
    </label>
  </form>
</template>

<i18n>
en:
  language: "🇺🇸 English"
fr:
  language: "🇫🇷 Français"
</i18n>

<style scoped>
form {
  display: inline;
}
</style>
