<script setup lang="ts">
import { useBreadcrumbsStore } from './BreadcrumbsStore'

const breadcrumbsStore = useBreadcrumbsStore()
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <p>
      <RouterLink :to="{ name: 'index' }">Patty home</RouterLink>
      <template v-for="breadcrumb in breadcrumbsStore.breadcrumbs">
        &gt;
        <RouterLink v-if="breadcrumb.to !== undefined" :to="breadcrumb.to">{{ breadcrumb.text }}</RouterLink>
        <template v-else>{{ breadcrumb.text }}</template>
      </template>
    </p>
  </div>
</template>

<style scoped>
div {
  background-color: rgb(210, 221, 238);
}

a {
  text-decoration: none;
  color: #007bff;
}
</style>
