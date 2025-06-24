<script setup lang="ts">
import { useApiConstantsStore } from './ApiConstantsStore'
import FrontendNavbar from './FrontendNavbar.vue'

const apiConstantsStore = useApiConstantsStore()
</script>

<template>
  <div class="container">
    <FrontendNavbar />
    <RouterView class="main" v-if="apiConstantsStore.ready" />
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main {
  flex: 1;
  overflow: auto;
}
</style>
