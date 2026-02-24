<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
defineProps<{
  busy: boolean
}>()
</script>

<template>
  <div style="position: relative">
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
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
