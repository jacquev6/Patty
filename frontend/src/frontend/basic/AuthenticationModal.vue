<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { useAuthenticationClient } from '../ApiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from '$/WhiteSpace.vue'
import LocaleSelect from './NavBarLocaleSelect.vue'

const client = useAuthenticationClient()
const tokenStore = useAuthenticationTokenStore()
const { t } = useI18n()

const password = ref('')
const message = ref<'incorrectPassword' | null>(null)

async function submit() {
  message.value = null
  const response = await client.POST('/api/token', {
    body: {
      password: password.value,
      validity: 'P1Y',
    },
  })
  if (response.response.ok) {
    tokenStore.set(response.data!.accessToken, new Date(response.data!.validUntil))
  } else {
    message.value = 'incorrectPassword'
  }
}
</script>

<template>
  <div class="modal">
    <div>
      <div style="display: flex; flex-direction: row">
        <div>
          <h1>{{ t('authentication') }}</h1>
        </div>
        <div style="flex: 1; min-width: 12em; text-align: end"><LocaleSelect /></div>
      </div>
      <p>
        {{ t('password') }} <input type="password" data-cy="password" v-model="password" />
        <WhiteSpace />
        <button data-cy="submit" @click="submit" :disabled="password === ''">{{ t('ok') }}</button>
      </p>
      <p v-if="message !== null">{{ t(message) }}</p>
    </div>
  </div>
</template>

<style scoped>
.modal {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
}

.modal > div {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
}
</style>

<i18n>
en:
  authentication: "Authentication"
  password: "Password:"
  ok: "OK"
  incorrectPassword: "Incorrect password."
fr:
  authentication: "Authentification"
  password: "Mot de passe:"
  ok: "OK"
  incorrectPassword: "Mot de passe incorrect."
</i18n>
