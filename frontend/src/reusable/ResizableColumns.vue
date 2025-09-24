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
