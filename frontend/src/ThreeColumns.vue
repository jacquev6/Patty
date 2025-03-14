<script setup lang="ts">
import Split from 'split-grid'
import { onMounted, useTemplateRef } from 'vue'

import assert from './assert'

const gutter1Ref = useTemplateRef('gutter1')
const gutter2Ref = useTemplateRef('gutter2')

onMounted(() => {
  assert(gutter1Ref.value !== null)
  assert(gutter2Ref.value !== null)

  Split({
    columnMinSize: 200,
    snapOffset: 0,
    columnGutters: [
      {
        track: 1,
        element: gutter1Ref.value,
      },
      {
        track: 3,
        element: gutter2Ref.value,
      },
    ],
  })
})
</script>

<template>
  <div class="columns">
    <div class="column">
      <slot name="left"></slot>
    </div>
    <div ref="gutter1" class="gutter"></div>
    <div class="column">
      <slot name="center"></slot>
    </div>
    <div ref="gutter2" class="gutter"></div>
    <div class="column">
      <slot name="right"></slot>
    </div>
  </div>
</template>

<style scoped>
.columns {
  display: grid;
  grid-template-columns: 1fr 8px 1fr 8px 1fr;
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
