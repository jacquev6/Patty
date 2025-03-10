<script setup lang="ts">
import { onMounted, ref } from 'vue'
import createClient from 'openapi-fetch'

import type { paths } from './openapi'

const client = createClient<paths>()

const who = ref<string>('<loading>')

async function update() {
  const res = await client.GET('/api')

  if (res.data !== undefined) {
    who.value = res.data.hello
  }
}

onMounted(update)
</script>

<template>
  <p>Hello {{ who }}!</p>
  <p><button @click="update">Update</button></p>
</template>
