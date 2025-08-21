<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { type PreviewableExercise } from './AdaptableExercisePreview.vue'
import WhiteSpace from './WhiteSpace.vue'
import { useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import ClassEditor from './EditClassificationOrExtractionBatchFormExercisePreviewClassEditor.vue'

const props = defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  exercise: PreviewableExercise
  showPageAndExercise: boolean
  rightColumn: { setFullScreen: () => void } | null
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
  (e: 'batch-updated'): void
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()
const identifiedUser = useIdentifiedUserStore()

const header = computed(() => `h${props.headerLevel}`)

const editingClassification = ref(false)

const exerciseClassProxy = computed({
  get: () =>
    props.exercise.kind === 'classificationOrExtraction' ? (props.exercise.exercise.exerciseClass ?? '') : '',
  async set(className: string) {
    if (props.exercise.kind === 'classificationOrExtraction' && className !== props.exercise.exercise.exerciseClass) {
      await client.PUT('/api/adaptable-exercises/{id}/exercise-class', {
        params: { path: { id: props.exercise.exercise.id } },
        body: { creator: identifiedUser.identifier, className },
      })
      emit('batch-updated')
    }
    editingClassification.value = false
  },
})
</script>

<template>
  <template v-if="exercise.kind === 'adaptation'">
    <slot>
      <component :is="header" style="margin-top: 0">
        Input {{ exercise.index + 1 }}
        <span v-if="exercise.adaptation.status.kind === 'inProgress'" class="inProgress">
          (in progress, will refresh when done)
        </span>
      </component>
      <p>
        Page: {{ exercise.adaptation.input.pageNumber ?? 'N/A' }}, exercise:
        {{ exercise.adaptation.input.exerciseNumber ?? 'N/A' }}
      </p>
    </slot>
    <p>
      <template v-for="(line, index) in exercise.adaptation.input.text">
        <br v-if="index !== 0" />
        {{ line }}
      </template>
    </p>
    <p>
      <button :disabled="exercise.adaptation.status.kind !== 'success'" @click="rightColumn?.setFullScreen()">
        Full screen
      </button>
    </p>
    <p>
      <RouterLink :to="{ name: 'adaptation', params: { id: exercise.adaptation.id } }">
        <button :disabled="exercise.adaptation.status.kind === 'inProgress'">View details and make adjustments</button>
      </RouterLink>
    </p>
  </template>
  <template v-else-if="exercise.kind === 'classificationOrExtraction'">
    <component :is="`h${headerLevel}`" style="margin-top: 0">
      {{ exercise.headerText
      }}<template v-if="exercise.classificationWasRequested">
        <span v-if="exercise.exercise.exerciseClass === null" class="inProgress"> ({{ t('inProgress') }})</span>
        <template v-else-if="editingClassification">: <ClassEditor v-model="exerciseClassProxy" /> </template>
        <template v-else>
          <template v-if="exercise.exercise.reclassifiedBy === null"
            >: {{ exercise.exercise.exerciseClass }}
            <span class="discrete"
              >({{ t('classifiedByModel') }} <span class="edit" @click="editingClassification = true">🖊️</span>)</span
            ></template
          >
          <template v-else
            >: {{ exercise.exercise.exerciseClass }}
            <span class="discrete"
              >({{ t('fixedBy') }} {{ exercise.exercise.reclassifiedBy }}
              <span class="edit" @click="editingClassification = true">🖊️</span>)</span
            ></template
          >
        </template>
      </template>
    </component>
    <p v-if="showPageAndExercise">
      {{
        t('pageAndExercise', {
          pageNumber: exercise.exercise.pageNumber ?? 'N/A',
          exerciseNumber: exercise.exercise.exerciseNumber ?? 'N/A',
        })
      }}
    </p>
    <p>
      <template v-for="(line, index) in exercise.exercise.fullText.split('\n')">
        <br v-if="index !== 0" />
        {{ line }}
      </template>
    </p>
    <template v-if="exercise.adaptation !== null">
      <p>
        <button :disabled="exercise.adaptation.status.kind !== 'success'" @click="rightColumn?.setFullScreen()">
          {{ t('fullScreen') }}
        </button>
      </p>
      <p>
        <RouterLink :to="{ name: 'adaptation', params: { id: exercise.adaptation.id } }">
          <button :disabled="exercise.adaptation.status.kind === 'inProgress'">{{ t('viewDetails') }}</button>
        </RouterLink>
      </p>
    </template>
  </template>
  <template v-else-if="exercise.kind === 'textbook'">
    <h5>
      Exercise {{ exercise.exercise.exerciseNumber
      }}<template v-if="exercise.exercise.exerciseClass === null">
        <WhiteSpace />
        <span class="inProgress">{{ t('inProgress') }}</span>
      </template>
      <template v-else
        >: {{ exercise.exercise.exerciseClass }}
        <button @click="emit('exercise-removed')">{{ t('remove') }}</button></template
      >
    </h5>
    <p>
      <template v-for="(line, index) in exercise.exercise.fullText.split('\n')">
        <br v-if="index !== 0" />
        {{ line }}
      </template>
    </p>
    <template v-if="exercise.adaptation !== null">
      <p>
        <button :disabled="exercise.adaptation.status.kind !== 'success'" @click="rightColumn?.setFullScreen()">
          {{ t('fullScreen') }}
        </button>
      </p>
      <p>
        <RouterLink :to="{ name: 'adaptation', params: { id: exercise.adaptation.id } }">
          <button :disabled="exercise.adaptation.status.kind === 'inProgress'">{{ t('viewDetails') }}</button>
        </RouterLink>
      </p>
    </template>
  </template>
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
</style>

<i18n>
en:
  classifiedByModel: classified by model
  fixedBy: fixed by
  pageAndExercise: "Page: {pageNumber}, exercise: {exerciseNumber}"
  inProgress: "in progress, will refresh when done"
  fullScreen: Full screen
  viewDetails: View details and make adjustments
  remove: Remove
fr:
  classifiedByModel: classifié par le modèle
  fixedBy: corrigé par
  pageAndExercise: "Page : {pageNumber}, exercice : {exerciseNumber}"
  inProgress: "en cours, se mettra à jour quand terminé"
  fullScreen: Plein écran
  viewDetails: Voir les détails et faire des ajustements
  remove: Enlever
</i18n>
