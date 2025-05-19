<script setup lang="ts">
import { ref } from 'vue'

import { useAuthenticationClient } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from './WhiteSpace.vue'

const client = useAuthenticationClient()
const tokenStore = useAuthenticationTokenStore()

const password = ref('')
const message = ref('')

async function submit() {
  message.value = ''
  const response = await client.POST('/api/token', {
    body: {
      password: password.value,
      validity: 'P1Y',
    },
  })
  if (response.response.ok) {
    tokenStore.set(response.data!.accessToken, new Date(response.data!.validUntil))
  } else {
    message.value = 'Incorrect password.'
  }
}
</script>

<template>
  <div class="modal">
    <div>
      <h1>Authentication</h1>
      <p>
        Password: <input type="password" data-cy="password" v-model="password" />
        <WhiteSpace />
        <button data-cy="submit" @click="submit" :disabled="password === ''">OK</button>
      </p>
      <p>{{ message }}</p>
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
