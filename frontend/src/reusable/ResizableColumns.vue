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
import Split from 'split-grid'
import { onMounted, ref, useTemplateRef, watch } from 'vue'

import assert from './assert'

const props = defineProps<{
  columns: {
    name: string
    width: number
  }[]
}>()

const gutters = useTemplateRef<HTMLDivElement[]>('gutters')

const gridTemplateColumns = ref(makeInitialGridTemplateColumns())
watch(
  () => props.columns,
  () => {
    gridTemplateColumns.value = makeInitialGridTemplateColumns()
  },
  { deep: true },
)

onMounted(async () => {
  assert(gutters.value !== null)

  Split({
    columnMinSize: 200,
    snapOffset: 0,
    columnGutters: gutters.value.map((gutter, gutterIndex) => ({
      track: 1 + 2 * gutterIndex,
      element: gutter,
    })),
  })
})

function makeInitialGridTemplateColumns() {
  const columns: string[] = []
  for (let index = 0; index < props.columns.length; index++) {
    columns.push(`${props.columns[index].width}fr`)
    if (index < props.columns.length - 1) {
      columns.push('8px')
    }
  }
  return columns.join(' ')
}
</script>

<template>
  <div class="columns" :style="{ gridTemplateColumns }">
    <template v-for="(column, columnIndex) in columns">
      <div v-if="columnIndex !== 0" ref="gutters" class="gutter"></div>
      <div class="column">
        <slot :name="column.name"></slot>
      </div>
    </template>
  </div>
</template>

<style scoped>
.columns {
  display: grid;
  height: 100%;
  overflow-y: hidden;
}

.gutter {
  background-color: black;
  border-left: 3px solid white;
  border-right: 3px solid white;
  cursor: col-resize;
}

.column {
  padding-left: 5px;
  padding-right: 5px;
  overflow-y: auto;
}
</style>
