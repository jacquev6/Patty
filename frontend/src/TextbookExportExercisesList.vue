<script setup lang="ts">
import { computed, ref } from 'vue'
import _ from 'lodash'

import PageNavigationControls from './AdaptedExercise/PageNavigationControls.vue'

const props = defineProps<{
  exercises: {
    exerciseId: string
    exerciseNumber: string
  }[]
}>()

const pageIndex = ref(0)
const pagesCount = computed(() => Math.ceil(props.exercises.length / 4))

const columns = computed(() => {
  const columns: ({ id: string; number: string } | null)[][] = _.chunk(
    props.exercises.map((e) => ({ number: e.exerciseNumber, id: e.exerciseId })),
    4,
  ).slice(pageIndex.value)
  const missing = 4 - columns[columns.length - 1]!.length
  for (let i = 0; i < missing; i++) {
    columns[columns.length - 1]!.push(null)
  }
  return columns
})
</script>

<template>
  <PageNavigationControls :navigateUsingArrowKeys="true" :pagesCount v-model="pageIndex">
    <div class="container">
      <div v-for="(column, columnIndex) in columns">
        <template v-for="exercise in column">
          <template v-if="exercise === null">
            <div class="exercise" style="visibility: hidden"><p>&nbsp;</p></div>
          </template>
          <template v-else>
            <RouterLink :to="{ name: 'exercise', params: { id: exercise.id } }" target="_blank">
              <div class="exercise" :class="`exercise${(pageIndex + columnIndex) % 3}`">
                <p>Exercice {{ exercise.number }}</p>
              </div>
            </RouterLink>
          </template>
        </template>
      </div>
    </div>
  </PageNavigationControls>
</template>

<style scoped>
.container {
  overflow-x: hidden;
  display: flex;
}

p {
  margin: 0;
}

a {
  text-decoration: none;
  color: inherit;
}

.exercise {
  margin: 2px;
  padding: 0.7em 2em;
  border-width: 2px;
  border-style: solid;
  border-radius: 5px;
  cursor: pointer;
  text-wrap-mode: nowrap;
  border-color: var(--color);
  color: var(--color);
}

.exercise:hover {
  background-color: #ccc;
}

.exercise0 {
  --color: #00f;
}

.exercise1 {
  --color: #0c0;
}

.exercise2 {
  --color: #f00;
}
</style>
