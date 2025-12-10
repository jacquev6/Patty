<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { onMounted } from 'vue'

import { useBreadcrumbsStore } from '@/frontend/basic/BreadcrumbsStore'
import CreateTextbookForm from './CreateTextbookForm.vue'

const breadcrumbsStore = useBreadcrumbsStore()

onMounted(() => {
  breadcrumbsStore.set([{ textKey: 'textbooks' }, { textKey: 'newTextbook', to: {} }])
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateTextbookForm />
  </div>
</template>
