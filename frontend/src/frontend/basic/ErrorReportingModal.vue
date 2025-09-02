<script setup lang="ts">
/// <reference types="user-agent-data-types" />

import { ref } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import { app } from '@/frontend/main'
import { useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'

const client = useAuthenticatedClient()
const identifierUser = useIdentifiedUserStore()
const { t } = useI18n()

const userAgent = (() => {
  if (window.navigator.userAgentData === undefined) {
    return window.navigator.userAgent
  } else {
    return JSON.stringify(window.navigator.userAgentData)
  }
})()
const { width: windowWidth, height: windowHeight } = useWindowSize()

function shortenStack(stack: string | undefined) {
  if (stack === undefined) {
    return null
  } else {
    return stack.split('\n').slice(0, 5).join('\n')
  }
}

type GlobalError = {
  caughtBy: string
  message: string
  codeLocation: string | null
}

const error = ref<GlobalError | null>(null)

async function reportError(e: GlobalError) {
  error.value = e
  await client.POST('/api/errors-caught-by-frontend', {
    body: {
      creator: identifierUser.identifier,
      userAgent,
      windowSize: `${windowWidth.value}x${windowHeight.value}`,
      url: window.location.href,
      ...e,
    },
  })
}

window.onerror = (message, source, lineno, colno) => {
  // @todo Deep dive into this issue: avoid the error instead of ignoring it.
  const ignored = message === 'ResizeObserver loop completed with undelivered notifications.' // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
  if (!ignored) {
    reportError({
      caughtBy: 'window.onerror',
      message: `${message}`,
      codeLocation: `${source}:${lineno}:${colno}`,
    })
  }
  return false
}

window.onunhandledrejection = (event) => {
  reportError({
    caughtBy: 'window.onunhandledrejection',
    message: `${event.reason}`,
    codeLocation: null,
  })
  return false
}

app.config.errorHandler = function (err, _vm, info) {
  reportError({
    caughtBy: 'Vue.config.errorHandler',
    message: `${err}\n${info}`,
    codeLocation: err instanceof Error ? shortenStack(err.stack) : null,
  })
}
</script>

<template>
  <div v-if="error !== null" class="backdrop">
    <div>
      <h1>{{ t('title') }}</h1>
      <p>{{ t('message1') }}</p>
      <p>{{ t('message2') }}</p>
      <pre>{{ error.message }}</pre>
      <pre>{{ error.codeLocation }}</pre>
    </div>
  </div>
</template>

<style scoped>
.backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.backdrop > div {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  background-color: white;
  border: 3px solid black;
  overflow: auto;
  padding: 1em;
}
</style>

<i18n>
en:
  title: There was a bug
  message1: It's not your fault. I (Vincent Jacques) have been notified and will look into it.
  message2: Your not-yet-submitted work is lost, I'm very sorry. You can only refresh the page and start over.
fr:
  title: Il y a eu un bug
  message1: Ce n'est pas de votre faute. J'ai (Vincent Jacques) été prévenu et je vais regarder ça.
  message2: Votre travail non encore soumis est perdu, je suis vraiment désolé. Vous pouvez seulement rafraîchir la page et recommencer.
</i18n>
