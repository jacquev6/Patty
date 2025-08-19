<script setup lang="ts">
import { type Textbook } from './apiClient'
import { useI18n } from 'vue-i18n'
import { computed, ref, watch } from 'vue'
import { useMagicKeys } from '@vueuse/core'

import FixedColumns from './FixedColumns.vue'
import WhiteSpace from './WhiteSpace.vue'
import { preprocess as preprocessAdaptation } from './adaptations'
import BusyBox from './BusyBox.vue'
import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

type Exercise = Textbook['ranges'][number]['pages'][number]['exercises'][number]

const props = defineProps<{
  exercise: Exercise
}>()

const { t } = useI18n()

const adaptation = computed(() => {
  if (props.exercise.adaptation === null) {
    return null
  } else {
    return preprocessAdaptation(props.exercise.adaptation)
  }
})

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
        <h5>
          Exercise {{ exercise.exerciseNumber
          }}<template v-if="exercise.exerciseClass === null">
            <WhiteSpace />
            <span class="inProgress">{{ t('inProgress') }}</span>
          </template>
          <template v-else>: {{ exercise.exerciseClass }} </template>
        </h5>
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
          <BusyBox v-if="exercise.exerciseClass == null" :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
          <p v-else-if="!exercise.exerciseClassHasSettings">
            <I18nT keypath="exerciseClassHasNoSettings"
              ><b>{{ exercise.exerciseClass }}</b></I18nT
            >
          </p>
        </template>
        <template v-else-if="adaptation.status.kind === 'inProgress'">
          <BusyBox :busy="true"><MiniatureScreen :fullScreen /></BusyBox>
        </template>
        <template v-else-if="adaptation.status.kind === 'error'">
          <h5 style="margin-top: 0">{{ t('errorWithLLM') }}</h5>
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
              {{ t('exitFullScreen') }}
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
</style>

<i18n>
en:
  inProgress: "in progress, will refresh when done"
  fullScreen: Full screen
  exitFullScreen: Exit full screen (Esc)
  viewDetails: View details and make adjustments
  exerciseClassHasNoSettings:
    "Exercise class {0} does not have adaptation settings yet."
  errorWithLLM: Error with the LLM
  llmInvalidJson: The LLM returned a JSON response that does not validate against the adapted exercise schema.
  llmNotJson: The LLM returned a response that is not correct JSON.
  llmUnknownError: The LLM caused an unknown error.
fr:
  inProgress: "en cours, se mettra à jour quand terminé"
  fullScreen: Plein écran
  exitFullScreen: Quitter le plein écran (Échap)
  viewDetails: Voir les détails et faire des ajustements
  exerciseClassHasNoSettings:
    "La classe d'exercice {0} n'a pas encore de paramètres d'adaptation."
  errorWithLLM: Erreur avec le LLM
  llmInvalidJson: Le LLM a renvoyé une réponse JSON qui ne correspond pas au schéma d'exercice adapté.
  llmNotJson: Le LLM a renvoyé une réponse qui n'est pas un JSON correct.
  llmUnknownError: Le LLM a causé une erreur inconnue.
</i18n>
