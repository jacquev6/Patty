<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import CreateClassificationBatchForm from './CreateClassificationBatchForm.vue'
import { useBreadcrumbsStore } from '@/frontend/basic/BreadcrumbsStore'
import { onMounted } from 'vue'

const breadcrumbsStore = useBreadcrumbsStore()

onMounted(() => {
  breadcrumbsStore.set([{ textKey: 'sandbox' }, { textKey: 'newClassificationBatch', to: {} }])
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateClassificationBatchForm />
  </div>
</template>
