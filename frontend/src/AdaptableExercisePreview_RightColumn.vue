<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'

import { type PreviewableExercise } from './AdaptableExercisePreview.vue'
import BugMarker from './BugMarker.vue'
import BusyBox from './BusyBox.vue'
import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

const props = defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  exercise: PreviewableExercise
}>()

const { t } = useI18n()

const header = computed(() => `h${props.headerLevel}`)

const fullScreen = ref(false)
const { Escape } = useMagicKeys()
watch(Escape, () => {
  fullScreen.value = false
})

defineExpose({
  setFullScreen() {
    fullScreen.value = true
  },
})
</script>

<template>
  <template v-if="exercise.kind === 'adaptation'">
    <template v-if="exercise.adaptation.status.kind === 'inProgress'">
      <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'error'">
      <component :is="header" style="margin-top: 0">Error with the LLM</component>
      <p>
        <template v-if="exercise.adaptation.status.error === 'invalid-json'">
          The LLM returned a JSON response that does not validate against the adapted exercise schema.
        </template>
        <template v-else-if="exercise.adaptation.status.error === 'not-json'">
          The LLM returned a response that is not correct JSON.
        </template>
        <template v-else-if="exercise.adaptation.status.error === 'unknown'">
          The LLM caused an unknown error.
        </template>
        <template v-else>BUG: {{ ((status: never) => status)(exercise.adaptation.status) }}</template>
      </p>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'success'">
      <MiniatureScreen :fullScreen>
        <AdaptedExerciseRenderer
          :navigateUsingArrowKeys="fullScreen"
          :adaptedExercise="exercise.adaptation.status.adaptedExercise"
        />
        <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">Exit full screen (Esc)</button>
      </MiniatureScreen>
    </template>
    <template v-else>
      <p>There was a bug: unexpected status: {{ ((status: never) => status)(exercise.adaptation.status) }}</p>
    </template>
  </template>
  <template v-else-if="exercise.kind === 'classificationOrExtraction'">
    <template v-if="exercise.adaptation === null">
      <p v-if="!exercise.adaptationWasRequested">{{ t('adaptationNotRequested') }}</p>
      <BusyBox v-else-if="exercise.exercise.exerciseClass == null" :busy="true"
        ><MiniatureScreen :fullScreen
      /></BusyBox>
      <p v-else-if="!exercise.exercise.exerciseClassHasSettings">
        <I18nT keypath="exerciseClassHasNoSettings"
          ><b>{{ exercise.exercise.exerciseClass }}</b></I18nT
        >
      </p>
      <template v-else>
        <p>
          <I18nT keypath="exerciseClassHadNoSettings"
            ><b>{{ exercise.exercise.exerciseClass }}</b></I18nT
          >
        </p>
        <p>
          <button @click="exercise.submitAdaptationsWithRecentSettings">{{ t('submitSimilarAdaptations') }}</button>
        </p>
      </template>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'inProgress'">
      <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'error'">
      <component :is="header" style="margin-top: 0">{{ t('errorWithLLM') }}</component>
      <p>
        <template v-if="exercise.adaptation.status.error === 'invalid-json'">{{ t('llmInvalidJson') }}</template>
        <template v-else-if="exercise.adaptation.status.error === 'not-json'">{{ t('llmNotJson') }}</template>
        <template v-else-if="exercise.adaptation.status.error === 'unknown'">{{ t('llmUnknownError') }}</template>
        <template v-else>BUG: {{ ((status: never) => status)(exercise.adaptation.status) }}</template>
      </p>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'success'">
      <MiniatureScreen :fullScreen>
        <AdaptedExerciseRenderer
          :navigateUsingArrowKeys="fullScreen"
          :adaptedExercise="exercise.adaptation.status.adaptedExercise"
        />
        <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">
          {{ t('exitFullScreen') }}
        </button>
      </MiniatureScreen>
    </template>
    <template v-else>
      <p>BUG: {{ ((status: never) => status)(exercise.adaptation.status) }}</p>
    </template>
  </template>
  <template v-else-if="exercise.kind === 'textbook'">
    <template v-if="exercise.adaptation === null">
      <BusyBox v-if="exercise.exercise.exerciseClass == null" :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
      <p v-else-if="!exercise.exercise.exerciseClassHasSettings">
        <I18nT keypath="exerciseClassHasNoSettings"
          ><b>{{ exercise.exercise.exerciseClass }}</b></I18nT
        >
      </p>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'inProgress'">
      <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'error'">
      <h5 style="margin-top: 0">{{ t('errorWithLLM') }}</h5>
      <p>
        <template v-if="exercise.adaptation.status.error === 'invalid-json'">{{ t('llmInvalidJson') }}</template>
        <template v-else-if="exercise.adaptation.status.error === 'not-json'">{{ t('llmNotJson') }}</template>
        <template v-else-if="exercise.adaptation.status.error === 'unknown'">{{ t('llmUnknownError') }}</template>
        <template v-else>BUG: {{ ((status: never) => status)(exercise.adaptation.status) }}</template>
      </p>
    </template>
    <template v-else-if="exercise.adaptation.status.kind === 'success'">
      <MiniatureScreen :fullScreen>
        <AdaptedExerciseRenderer
          :navigateUsingArrowKeys="fullScreen"
          :adaptedExercise="exercise.adaptation.status.adaptedExercise"
        />
        <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">
          {{ t('exitFullScreen') }}
        </button>
      </MiniatureScreen>
    </template>
    <template v-else>
      <p>BUG: {{ ((status: never) => status)(exercise.adaptation.status) }}</p>
    </template>
  </template>
  <BugMarker :is="header" v-else m="unexpected previewable exercise kind" :v="exercise" />
</template>

<style scoped>
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
  remove: Remove
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
  remove: Enlever
</i18n>
