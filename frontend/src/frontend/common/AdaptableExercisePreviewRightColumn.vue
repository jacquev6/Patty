<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'

import { type PreviewableExercise, type Context } from './AdaptableExercisePreview.vue'
import BugMarker from '$/BugMarker.vue'
import BusyBox from '$/BusyBox.vue'
import MiniatureScreen from '$/MiniatureScreen.vue'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { type AdaptationLlmModel } from '@/frontend/ApiClient'
import WhiteSpace from '@/reusable/WhiteSpace.vue'

const props = defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  exercise: PreviewableExercise
  context: Context
  availableAdaptationLlmModels: AdaptationLlmModel[]
}>()

const emit = defineEmits<{
  (e: 'submit-extractions-with-recent-settings'): void
  (e: 'submit-extractions-with-recent-settings-using', model: AdaptationLlmModel): void
}>()

const { t } = useI18n()

const header = computed(() => `h${props.headerLevel}`)

const modelForAdaptation = ref<AdaptationLlmModel>(props.availableAdaptationLlmModels[0])

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
  <template v-if="exercise.adaptationStatus.kind === 'notRequested'">
    <p>{{ t('adaptationNotRequested') }}</p>
  </template>
  <template v-else-if="exercise.adaptationStatus.kind === 'notStarted'">
    <template v-if="exercise.classificationStatus.kind === 'notRequested'">
      <!-- @todo Display something? -->
    </template>
    <template v-else-if="exercise.classificationStatus.kind === 'inProgress'">
      <BusyBox :busy="true"><MiniatureScreen :fullScreen="false" /></BusyBox>
    </template>
    <template
      v-else-if="exercise.classificationStatus.kind === 'byModel' || exercise.classificationStatus.kind === 'byUser'"
    >
      <template v-if="exercise.classificationStatus.classHasSettings">
        <p>
          <I18nT keypath="exerciseClassHadNoSettings">
            <b>{{ exercise.classificationStatus.exerciseClass }}</b>
          </I18nT>
        </p>
        <p v-if="context === 'extraction' || context === 'classification'">
          <button @click="emit('submit-extractions-with-recent-settings')">{{ t('submitSimilarAdaptations') }}</button>
        </p>
        <p v-else-if="context === 'textbook'">
          <I18nT keypath="useModelToSubmitSimilarAdaptations">
            <LlmModelSelector
              :availableLlmModels="availableAdaptationLlmModels"
              :disabled="false"
              v-model="modelForAdaptation"
            >
              <template #provider><WhiteSpace /></template>
            </LlmModelSelector>

            <button @click="emit('submit-extractions-with-recent-settings-using', modelForAdaptation)">
              {{ t('submitSimilarAdaptations') }}
            </button>
          </I18nT>
        </p>
      </template>
      <template v-else>
        <p>
          <I18nT keypath="exerciseClassHasNoSettings">
            <b>{{ exercise.classificationStatus.exerciseClass }}</b>
          </I18nT>
        </p>
      </template>
    </template>
    <BugMarker v-else :is="header" m="unexpected classification status" :v="exercise.classificationStatus" />
  </template>
  <template v-else-if="exercise.adaptationStatus.kind === 'inProgress'">
    <BusyBox :busy="true"><MiniatureScreen :fullScreen="false" /></BusyBox>
  </template>
  <template v-else-if="exercise.adaptationStatus.kind === 'error'">
    <component :is="header" style="margin-top: 0">{{ t('errorWithLLM') }}</component>
    <p>
      <template v-if="exercise.adaptationStatus.error === 'invalid-json'">
        {{ t('llmInvalidJson') }}
      </template>
      <template v-else-if="exercise.adaptationStatus.error === 'not-json'">
        {{ t('llmNotJson') }}
      </template>
      <template v-else-if="exercise.adaptationStatus.error === 'unknown'">
        {{ t('llmUnknownError') }}
      </template>
      <BugMarker v-else is="span" m="unexpected adaptation error" :v="exercise.adaptationStatus" />
    </p>
  </template>
  <template v-else-if="exercise.adaptationStatus.kind === 'success'">
    <MiniatureScreen :fullScreen>
      <AdaptedExerciseRenderer
        :navigateUsingArrowKeys="fullScreen"
        :adaptedExercise="exercise.adaptationStatus.adaptedExercise"
        :imagesUrls="exercise.imagesUrls"
      />
      <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">{{ t('exitFullScreen') }}</button>
    </MiniatureScreen>
  </template>
  <BugMarker v-else :is="header" m="unexpected adaptation status" :v="exercise.adaptationStatus" />
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
  exitFullScreen: Exit full screen (Esc)
  adaptationNotRequested: Adaptation was not requested.
  exerciseClassHasNoSettings: "Exercise class {0} does not have adaptation settings yet."
  exerciseClassHadNoSettings: "Exercise class {0} did not have adaptation settings when this exercise was created."
  useModelToSubmitSimilarAdaptations: 'Use {0} to {1}'
  submitSimilarAdaptations: Submit all adaptations in the same case
  errorWithLLM: Error with the LLM
  llmInvalidJson: The LLM returned a JSON response that does not validate against the adapted exercise schema.
  llmNotJson: The LLM returned a response that is not correct JSON.
  llmUnknownError: The LLM caused an unknown error.
fr:
  exitFullScreen: Quitter le plein écran (Échap)
  adaptationNotRequested: L'adaptation n'a pas été demandée.
  exerciseClassHasNoSettings: "La classe d'exercice {0} n'a pas encore de paramètres d'adaptation."
  exerciseClassHadNoSettings: "La classe d'exercice {0} n'avait pas de paramètres d'adaptation lorsque cet exercice a été créé."
  useModelToSubmitSimilarAdaptations: 'Utiliser {0} pour {1}'
  submitSimilarAdaptations: Soumettre toutes les adaptations dans le même cas
  errorWithLLM: Erreur avec le LLM
  llmInvalidJson: Le LLM a renvoyé une réponse JSON qui ne correspond pas au schéma d'exercice adapté.
  llmNotJson: Le LLM a renvoyé une réponse qui n'est pas un JSON correct.
  llmUnknownError: Le LLM a causé une erreur inconnue.
</i18n>
