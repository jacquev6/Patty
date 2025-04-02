<script setup lang="ts">
import Split from 'split-grid'
import { onMounted, ref, useTemplateRef } from 'vue'

import assert from './assert'

const props = defineProps<{
  columns: number // Not reactive yet
}>()

const gutters = useTemplateRef<HTMLDivElement[]>('gutters')

const gridTemplateColumns = ref('')

onMounted(async () => {
  assert(gutters.value !== null)

  gridTemplateColumns.value = makeInitialGridTemplateColumns()

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
  for (let i = 0; i < props.columns; i++) {
    columns.push('1fr')
    if (i < props.columns - 1) {
      columns.push('8px')
    }
  }
  return columns.join(' ')
}
</script>

<template>
  <div class="columns" :style="{ gridTemplateColumns }">
    <template v-for="column of columns">
      <div v-if="column !== 1" ref="gutters" class="gutter"></div>
      <div class="column">
        <slot :name="`col-${column}`"></slot>
      </div>
    </template>
  </div>
</template>

<style scoped>
.columns {
  display: grid;
  height: 100vh;
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
  overflow-y: scroll;
}
</style>
