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
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    columns: number[]
    gutters?: boolean
  }>(),
  {
    gutters: true,
  },
)

const gridTemplateColumns = computed(() => {
  const columns: string[] = []
  for (let index = 0; index < props.columns.length; index++) {
    columns.push(`${props.columns[index]}fr`)
    if (index < props.columns.length - 1) {
      columns.push(props.gutters ? '7px' : '6px')
    }
  }
  return columns.join(' ')
})
</script>

<template>
  <div class="columns" :style="{ gridTemplateColumns }">
    <template v-for="column of columns.length">
      <div v-if="column !== 1" class="gutter"></div>
      <div class="column">
        <slot :name="`col-${column}`"></slot>
      </div>
    </template>
  </div>
</template>

<style scoped>
.columns {
  display: grid;
}

.gutter {
  background-color: black;
  border-left: 3px solid white;
  border-right: 3px solid white;
}

.column {
  overflow-x: hidden;
}
</style>
