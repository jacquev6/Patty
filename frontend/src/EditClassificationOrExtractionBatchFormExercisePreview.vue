<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import FixedColumns from './FixedColumns.vue'
import { preprocess as preprocessAdaptation } from './adaptations'
import BusyBox from './BusyBox.vue'
import { useAuthenticatedClient, type ClassificationBatch } from './apiClient'
import EditClassificationBatchFormExercisePreviewClassEditor from './EditClassificationOrExtractionBatchFormExercisePreviewClassEditor.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { match } from 'ts-pattern'

type BatchId = {
  kind: 'classification' | 'extraction'
  id: string
}

const props = defineProps<{
  batch: BatchId
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
const { t } = useI18n()

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

async function submitAdaptationsWithRecentSettings() {
  await match(props.batch)
    .with({ kind: 'classification' }, () =>
      client.POST(`/api/classification-batches/{id}/submit-adaptations-with-recent-settings`, {
        params: { path: { id: props.batch.id } },
      }),
    )
    .with({ kind: 'extraction' }, () =>
      client.POST(`/api/extraction-batches/{id}/submit-adaptations-with-recent-settings`, {
        params: { path: { id: props.batch.id } },
      }),
    )
    .exhaustive()
  emit('batch-updated')
}
</script>

<template>
  <div style="margin-top: 5px">
    <FixedColumns :columns="[1, 1]" :gutters="false">
      <template #col-1>
        <component :is="headerComponent" style="margin-top: 0">
          {{ headerText
          }}<template v-if="classificationWasRequested">
            <span v-if="exercise.exerciseClass === null" class="inProgress"> ({{ t('inProgress') }})</span>
            <template v-else-if="editingClassification"
              >: <EditClassificationBatchFormExercisePreviewClassEditor v-model="exerciseClassProxy" />
            </template>
            <template v-else>
              <template v-if="exercise.reclassifiedBy === null"
                >: {{ exercise.exerciseClass }}
                <span class="discrete"
                  >({{ t('classifiedByModel') }}
                  <span class="edit" @click="editingClassification = true">🖊️</span>)</span
                ></template
              >
              <template v-else
                >: {{ exercise.exerciseClass }}
                <span class="discrete"
                  >({{ t('fixedBy') }} {{ exercise.reclassifiedBy }}
                  <span class="edit" @click="editingClassification = true">🖊️</span>)</span
                ></template
              >
            </template>
          </template>
        </component>
        <p v-if="showPageAndExercise">
          {{
            t('pageAndExercise', {
              pageNumber: exercise.pageNumber ?? 'N/A',
              exerciseNumber: exercise.exerciseNumber ?? 'N/A',
            })
          }}
        </p>
        <p>
          <template v-for="(line, index) in exercise.fullText.split('\n')">
            <br v-if="index !== 0" />
            {{ line }}
          </template>
        </p>
        <template v-if="adaptation !== null">
          <p>
            <button :disabled="adaptation.status.kind !== 'success'" @click="fullScreen = true">
              {{ t('fullScreen') }}
            </button>
          </p>
          <p>
            <RouterLink :to="{ name: 'adaptation', params: { id: adaptation.id } }">
              <button :disabled="adaptation.status.kind === 'inProgress'">{{ t('viewDetails') }}</button>
            </RouterLink>
          </p>
        </template>
      </template>
      <template #col-2>
        <template v-if="adaptation === null">
          <p v-if="!adaptationWasRequested">{{ t('adaptationNotRequested') }}</p>
          <BusyBox v-else-if="exercise.exerciseClass == null" :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
          <p v-else-if="!exercise.exerciseClassHasSettings">
            <I18nT keypath="exerciseClassHasNoSettings"
              ><b>{{ exercise.exerciseClass }}</b></I18nT
            >
          </p>
          <template v-else>
            <p>
              <I18nT keypath="exerciseClassHadNoSettings"
                ><b>{{ exercise.exerciseClass }}</b></I18nT
              >
            </p>
            <p>
              <button @click="submitAdaptationsWithRecentSettings">{{ t('submitSimilarAdaptations') }}</button>
            </p>
          </template>
        </template>
        <template v-else-if="adaptation.status.kind === 'inProgress'">
          <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
        </template>
        <template v-else-if="adaptation.status.kind === 'error'">
          <component :is="headerComponent" style="margin-top: 0">{{ t('errorWithLLM') }}</component>
          <p>
            <template v-if="adaptation.status.error === 'invalid-json'">{{ t('llmInvalidJson') }}</template>
            <template v-else-if="adaptation.status.error === 'not-json'">{{ t('llmNotJson') }}</template>
            <template v-else-if="adaptation.status.error === 'unknown'">{{ t('llmUnknownError') }}</template>
            <template v-else>BUG: {{ ((status: never) => status)(adaptation.status) }}</template>
          </p>
        </template>
        <template v-else-if="adaptation.status.kind === 'success'">
          <MiniatureScreen :fullScreen>
            <AdaptedExerciseRenderer
              :navigateUsingArrowKeys="fullScreen"
              :adaptedExercise="adaptation.status.adaptedExercise"
            />
            <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">
              {{ t('existFullScreen') }}
            </button>
          </MiniatureScreen>
        </template>
        <template v-else>
          <p>BUG: {{ ((status: never) => status)(adaptation.status) }}</p>
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

<i18n>
en:
  inProgress: "in progress, will refresh when done"
  classifiedByModel: classified by model
  fixedBy: fixed by
  pageAndExercise: "Page: {pageNumber}, exercise: {exerciseNumber}"
  fullScreen: Full screen
  exitFullScreen: Exit full screen (Esc)
  viewDetails: View details and make adjustments
  adaptationNotRequested: Adaptation was not requested.
  exerciseClassHasNoSettings:
    "Exercise class {0} does not have adaptation settings yet."
  exerciseClassHadNoSettings:
    "Exercise class {0} did not have adaptation settings when this classification batch was submitted."
  submitSimilarAdaptations: Submit all adaptations in the same case
  errorWithLLM: Error with the LLM
  llmInvalidJson: The LLM returned a JSON response that does not validate against the adapted exercise schema.
  llmNotJson: The LLM returned a response that is not correct JSON.
  llmUnknownError: The LLM caused an unknown error.
fr:
  inProgress: "en cours, se mettra à jour quand terminé"
  classifiedByModel: classifié par le modèle
  fixedBy: corrigé par
  pageAndExercise: "Page : {pageNumber}, exercice : {exerciseNumber}"
  fullScreen: Plein écran
  exitFullScreen: Quitter le plein écran (Échap)
  viewDetails: Voir les détails et faire des ajustements
  adaptationNotRequested: L'adaptation n'a pas été demandée.
  exerciseClassHasNoSettings:
    "La classe d'exercice {0} n'a pas encore de paramètres d'adaptation."
  exerciseClassHadNoSettings:
    "La classe d'exercice {0} n'avait pas de paramètres d'adaptation
    lorsque ce batch de classification a été soumis."
  submitSimilarAdaptations: Soumettre toutes les adaptations dans le même cas
  errorWithLLM: Erreur avec le LLM
  llmInvalidJson: Le LLM a renvoyé une réponse JSON qui ne correspond pas au schéma d'exercice adapté.
  llmNotJson: Le LLM a renvoyé une réponse qui n'est pas un JSON correct.
  llmUnknownError: Le LLM a causé une erreur inconnue.
</i18n>
