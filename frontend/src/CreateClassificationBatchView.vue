<script setup lang="ts">
import CreateClassificationBatchForm from './CreateClassificationBatchForm.vue'
import { useBreadcrumbsStore } from './BreadcrumbsStore'
import { onMounted } from 'vue'

const breadcrumbsStore = useBreadcrumbsStore()

onMounted(() => {
  breadcrumbsStore.set([{ text: 'Sandbox' }, { text: 'New classification batch', to: {} }])
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateClassificationBatchForm />
  </div>
</template>
