<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'

import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import FixedColumns from './FixedColumns.vue'
import type { PreprocessedAdaptation } from './adaptations'
import BusyBox from './BusyBox.vue'

defineProps<{
  index: number
  adaptation: PreprocessedAdaptation
}>()

const fullScreen = ref(false)

const { Escape } = useMagicKeys()

watch(Escape, () => {
  fullScreen.value = false
})
</script>

<template>
  <div style="margin-top: 5px">
    <FixedColumns :columns="[1, 1]" :gutters="false">
      <template #col-1>
        <h2>
          Input {{ index + 1 }}
          <span v-if="adaptation.status.kind === 'inProgress'" class="inProgress">
            (in progress, will refresh when done)
          </span>
        </h2>
        <p>
          Page: {{ adaptation.input.pageNumber ?? 'N/A' }}, exercise: {{ adaptation.input.exerciseNumber ?? 'N/A' }}
        </p>
        <p>
          <template v-for="(line, index) in adaptation.input.text">
            <br v-if="index !== 0" />
            {{ line }}
          </template>
        </p>
        <p><button :disabled="adaptation.status.kind !== 'success'" @click="fullScreen = true">Full screen</button></p>
        <p>
          <RouterLink :to="{ name: 'adaptation', params: { id: adaptation.id } }">
            <button :disabled="adaptation.status.kind === 'inProgress'">View details and make adjustments</button>
          </RouterLink>
        </p>
      </template>
      <template #col-2>
        <template v-if="adaptation.status.kind === 'inProgress'">
          <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
        </template>
        <template v-else-if="adaptation.status.kind === 'error'">
          <h2>Error with the LLM</h2>
          <p>
            <template v-if="adaptation.status.error === 'invalid-json'">
              The LLM returned a JSON response that does not validate against the adapted exercise schema.
            </template>
            <template v-else-if="adaptation.status.error === 'not-json'">
              The LLM returned a response that is not correct JSON.
            </template>
            <template v-else>BUG: {{ ((status: never) => status)(adaptation.status) }}</template>
          </p>
        </template>
        <template v-else-if="adaptation.status.kind === 'success'">
          <MiniatureScreen :fullScreen>
            <AdaptedExerciseRenderer
              :navigateUsingArrowKeys="fullScreen"
              :adaptedExercise="adaptation.status.adaptedExercise"
            />
            <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">Exit full screen (Esc)</button>
          </MiniatureScreen>
        </template>
        <template v-else>
          <p>There was a bug: unexpected status: {{ ((status: never) => status)(adaptation.status) }}</p>
        </template>
      </template>
    </FixedColumns>
  </div>
</template>

<style scoped>
h2 {
  margin-top: 0;
}

span.inProgress {
  color: gray;
  font-size: 70%;
}

button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
