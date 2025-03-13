<script setup lang="ts">
defineProps<{
  busy: boolean
}>()
</script>

<template>
  <div style="position: relative;">
    <slot></slot>
    <div v-if="busy" class="busy"><div class="spinner"></div></div>
  </div>
</template>

<style scoped>
.busy {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.spinner {
  position: absolute;
  top: calc(50% - 60px);
  left: calc(50% - 60px);
  border: 16px solid lightgray;
  border-top: 16px solid darkgray;
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2000ms infinite linear; 
}

@keyframes spin {
  from {
    transform:rotate(0deg);
  }
  to {
    transform:rotate(360deg);
  }
}
</style>
