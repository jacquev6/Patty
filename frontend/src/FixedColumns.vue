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
