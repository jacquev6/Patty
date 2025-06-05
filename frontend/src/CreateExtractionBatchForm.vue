<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import shajs from 'sha.js'

import { type LlmModel, useAuthenticatedClient } from './apiClient'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import assert from './assert'

defineProps<{
  availableLlmModels: LlmModel[]
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const uploading = ref(false)
const uploadedFileSha256 = ref<string | null>(null)
const disabled = computed(() => uploadedFileSha256.value === null)

async function openFile(event: Event) {
  uploadedFileSha256.value = null

  const input = event.target as HTMLInputElement
  assert(input.files !== null)
  if (input.files.length == 1) {
    const file = input.files[0]

    const startTime = performance.now()
    const sha256 = shajs('sha256')
      .update(new Uint8Array(await file.arrayBuffer()))
      .digest('hex')
    console.info(`Computed sha256=${sha256} in ${Math.round(performance.now() - startTime)}ms`)

    const response = await client.POST('/api/pdf-files', {
      body: {
        sha256,
        creator: identifiedUser.identifier,
        fileName: file.name,
        bytesCount: file.size,
      },
    })
    assert(response.data !== undefined)
    const uploadUrl = response.data.uploadUrl
    if (uploadUrl !== null) {
      uploading.value = true
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      })
      assert(uploadResponse.status === 200)
      uploading.value = false
    }
    uploadedFileSha256.value = sha256
  }
}

async function submit() {
  const response = await client.POST('/api/extraction-batches', {
    body: {
      creator: identifiedUser.identifier,
    },
  })
  if (response.data !== undefined) {
    router.push({ name: 'extraction-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p>
    PDF file: <input type="file" @change="openFile" accept=".pdf" :disabled="uploading" />
    <template v-if="uploading"> (uploading...)</template>
    <template v-if="uploadedFileSha256 !== null"> (uploaded)</template>
  </p>
  <p><button @click="submit" :disabled>Submit</button></p>
</template>
