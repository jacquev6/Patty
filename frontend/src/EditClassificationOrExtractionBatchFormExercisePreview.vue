<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'

import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import FixedColumns from './FixedColumns.vue'
import { preprocess as preprocessAdaptation } from './adaptations'
import BusyBox from './BusyBox.vue'
import { useAuthenticatedClient, type ClassificationBatch } from './apiClient'
import EditClassificationBatchFormExercisePreviewClassEditor from './EditClassificationOrExtractionBatchFormExercisePreviewClassEditor.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const props = defineProps<{
  headerComponent: string
  headerText: string
  showPageAndExercise: boolean
  classificationWasRequested: boolean
  adaptationWasRequested: boolean
  exercise: ClassificationBatch['exercises'][number]
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const client = useAuthenticatedClient()
const identifiedUser = useIdentifiedUserStore()

const adaptation = computed(() => {
  if (props.exercise.adaptation === null) {
    return null
  } else {
    return preprocessAdaptation(props.exercise.adaptation)
  }
})

const fullScreen = ref(false)

const editingClassification = ref(false)

const exerciseClassProxy = computed({
  get: () => props.exercise.exerciseClass ?? '',
  async set(className: string) {
    if (className !== props.exercise.exerciseClass) {
      await client.PUT('/api/adaptable-exercises/{id}/exercise-class', {
        params: { path: { id: props.exercise.id } },
        body: { creator: identifiedUser.identifier, className },
      })
      emit('batch-updated')
    }
    editingClassification.value = false
  },
})

const { Escape } = useMagicKeys()

watch(Escape, () => {
  fullScreen.value = false
})
</script>

<template>
  <div style="margin-top: 5px">
    <FixedColumns :columns="[1, 1]" :gutters="false">
      <template #col-1>
        <component :is="headerComponent" style="margin-top: 0">
          {{ headerText
          }}<template v-if="classificationWasRequested">
            <span v-if="exercise.exerciseClass === null" class="inProgress">
              (in progress, will refresh when done)
            </span>
            <template v-else-if="editingClassification"
              >: <EditClassificationBatchFormExercisePreviewClassEditor v-model="exerciseClassProxy" />
            </template>
            <template v-else>
              <template v-if="exercise.reclassifiedBy === null"
                >: {{ exercise.exerciseClass }}
                <span class="discrete"
                  >(classified by model <span class="edit" @click="editingClassification = true">🖊️</span>)</span
                ></template
              >
              <template v-else
                >: {{ exercise.exerciseClass }}
                <span class="discrete"
                  >(fixed by {{ exercise.reclassifiedBy }}
                  <span class="edit" @click="editingClassification = true">🖊️</span>)</span
                ></template
              >
            </template>
          </template>
        </component>
        <p v-if="showPageAndExercise">
          Page: {{ exercise.pageNumber ?? 'N/A' }}, exercise: {{ exercise.exerciseNumber ?? 'N/A' }}
        </p>
        <p>
          <template v-for="(line, index) in exercise.fullText.split('\n')">
            <br v-if="index !== 0" />
            {{ line }}
          </template>
        </p>
        <template v-if="adaptation !== null">
          <p>
            <button :disabled="adaptation.status.kind !== 'success'" @click="fullScreen = true">Full screen</button>
          </p>
          <p>
            <RouterLink :to="{ name: 'adaptation', params: { id: adaptation.id } }">
              <button :disabled="adaptation.status.kind === 'inProgress'">View details and make adjustments</button>
            </RouterLink>
          </p>
        </template>
      </template>
      <template #col-2>
        <template v-if="adaptation === null">
          <p v-if="!adaptationWasRequested">Adaptation was not requested.</p>
          <BusyBox v-else-if="exercise.exerciseClass == null" :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
          <p v-else-if="!exercise.exerciseClassHasSettings">
            Exercise class <b>{{ exercise.exerciseClass }}</b> does not have adaptation settings yet.
          </p>
          <p v-else>
            Exercise class <b>{{ exercise.exerciseClass }}</b> did not have adaptation settings when this classification
            batch was submitted.
          </p>
        </template>
        <template v-else-if="adaptation.status.kind === 'inProgress'">
          <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
        </template>
        <template v-else-if="adaptation.status.kind === 'error'">
          <component :is="headerComponent" style="margin-top: 0">Error with the LLM</component>
          <p>
            <template v-if="adaptation.status.error === 'invalid-json'">
              The LLM returned a JSON response that does not validate against the adapted exercise schema.
            </template>
            <template v-else-if="adaptation.status.error === 'not-json'">
              The LLM returned a response that is not correct JSON.
            </template>
            <template v-else-if="adaptation.status.error === 'unknown'"> The LLM caused an unknown error. </template>
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
span.inProgress {
  color: gray;
  font-size: 70%;
}

span.discrete {
  color: gray;
}

span.edit {
  cursor: pointer;
}

button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
