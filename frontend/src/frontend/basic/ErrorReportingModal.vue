<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

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

const errorsCount = ref(0)
const error = ref<GlobalError | null>(null)
function isNetworkError(e: GlobalError): boolean {
  return (
    e.message.startsWith('TypeError: Failed to fetch') ||
    e.message.startsWith('TypeError: NetworkError when attempting to fetch resource.')
  )
}

async function reportError(e: GlobalError) {
  errorsCount.value += 1
  if (errorsCount.value === 1) {
    console.error('Reporting error', e)
    error.value = e
    await client.POST('/api/errors-caught-by-frontend', {
      body: {
        creator: identifierUser.identifier,
        userAgent,
        windowSize: `${windowWidth.value}x${windowHeight.value}`,
        url: window.location.href,
        ...e,
        githubIssueNumber: isNetworkError(e) ? 99 : null,
      },
    })
  } else {
    console.error('An error is already being reported, ignoring', e)
  }
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
    <div v-if="isNetworkError(error)">
      <h1>{{ t('network.title') }}</h1>
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-v-html -->
      <p v-html="t('network.message1')"></p>
      <p>{{ t('network.message2') }}</p>
    </div>
    <div v-else>
      <h1>
        {{ t('bug.title') }}
        <template v-if="errorsCount !== 1"> {{ t('bug.occurrences', { count: errorsCount }) }}</template>
      </h1>
      <p>{{ t('bug.message1') }}</p>
      <p>{{ t('bug.message2') }}</p>
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
  bug:
    title: There was a bug
    occurrences: " ({count} occurrences)"
    message1: It's not your fault. I (Vincent Jacques) have been notified and will look into it.
    message2: Your not-yet-submitted work is lost, I'm very sorry. You can only refresh the page and start over.
  network:
    title: There was a network error
    message1: "Are you on a weak internet connection? If this happens often, you may want to increase the priority of <a href=\"https://github.com/jacquev6/Patty/issues/99\">issue #99</a>."
    message2: Your not-yet-submitted work is lost, I'm very sorry. You can only refresh the page and start over.
fr:
  bug:
    title: Il y a eu un bug
    occurrences: " ({count} occurrences)"
    message1: Ce n'est pas de votre faute. J'ai (Vincent Jacques) été prévenu et je vais regarder ça.
    message2: Votre travail non encore soumis est perdu, je suis vraiment désolé. Vous pouvez seulement rafraîchir la page et recommencer.
  network:
    title: Il y a eu une erreur réseau
    message1: "Êtes-vous sur une connexion internet fragile ? Si cela arrive souvent, vous pouvez augmenter la priorité de <a href=\"https://github.com/jacquev6/Patty/issues/99\">l'issue #99</a>."
    message2: Votre travail non encore soumis est perdu, je suis vraiment désolé. Vous pouvez seulement rafraîchir la page et recommencer.
</i18n>
