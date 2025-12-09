<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { type PreviewableExercise, type Context } from './AdaptableExercisePreview.vue'
import WhiteSpace from '$/WhiteSpace.vue'
import { useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import ClassEditor from '@/frontend/common/AdaptableExercisePreviewLeftColumnClassEditor.vue'

const props = defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  exercise: PreviewableExercise
  context: Context
  index: number | null
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
    props.exercise.classificationStatus.kind === 'byModel' || props.exercise.classificationStatus.kind === 'byUser'
      ? props.exercise.classificationStatus.exerciseClass
      : '',
  async set(className: string) {
    if (
      props.exercise.classificationStatus.kind === 'byModel' ||
      (props.exercise.classificationStatus.kind === 'byUser' &&
        className !== props.exercise.classificationStatus.exerciseClass)
    ) {
      await client.PUT('/api/adaptable-exercises/{id}/exercise-class', {
        params: { path: { id: props.exercise.id } },
        body: { creator: identifiedUser.identifier, className },
      })
      emit('batch-updated')
    }
    editingClassification.value = false
  },
})

const fullTextLines = computed(() => props.exercise.fullText.split('\n'))

const pageNumber = computed(() => props.exercise.pageNumber)

const exerciseNumber = computed(() => props.exercise.exerciseNumber)

async function approve(adaptationId: string, approved: boolean) {
  await client.PUT('/api/adaptations/{id}/approved', {
    params: { path: { id: adaptationId } },
    body: { approved, by: identifiedUser.identifier },
  })
  emit('batch-updated')
}

function isStringyInt(value: string): boolean {
  return !isNaN(Number.parseInt(value))
}
</script>

<template>
  <component :is="header" style="margin-top: 0">
    <template v-if="index !== null">{{ t('input') }} {{ index + 1 }}</template>
    <template v-else-if="exercise.exerciseNumber !== null && isStringyInt(exercise.exerciseNumber)">
      {{ t('exercise') }} {{ exercise.exerciseNumber }}
    </template>
    <template v-else>{{ exercise.exerciseNumber }}</template>

    <template v-if="exercise.classificationStatus.kind !== 'notRequested'">
      <template v-if="exercise.classificationStatus.kind === 'inProgress'">
        <WhiteSpace />
        <span class="inProgress">({{ t('inProgress') }})</span>
      </template>
      <template v-else-if="editingClassification"
        >: <ClassEditor v-model="exerciseClassProxy" @done="editingClassification = false" />
      </template>
      <template v-else
        >: {{ exercise.classificationStatus.exerciseClass }}
        <template v-if="context === 'classification' || context === 'extraction'">
          <template v-if="exercise.classificationStatus.kind === 'byModel'">
            <span class="discrete">
              ({{ t('classifiedByModel') }} <span class="edit" @click="editingClassification = true">🖊️</span>)
            </span>
          </template>
          <template v-else>
            <span class="discrete">
              ({{ t('fixedBy') }} {{ exercise.classificationStatus.by }}
              <span class="edit" @click="editingClassification = true">🖊️</span>)
            </span>
          </template>
        </template>
        <template v-else-if="context === 'textbook'">
          <span class="discrete">(<span class="edit" @click="editingClassification = true">🖊️</span>)</span>
          <WhiteSpace />
          <button @click="emit('exercise-removed')">{{ t('remove') }}</button>
        </template>
        <template v-if="context === 'textbook' && exercise.adaptationStatus.kind === 'success'">
          <WhiteSpace />
          <template v-if="exercise.adaptationStatus.approved === null">
            <button @click="approve(exercise.adaptationStatus.id, true)">{{ t('approve') }}</button>
          </template>
          <template v-else>
            <button @click="approve(exercise.adaptationStatus.id, false)">{{ t('unapprove') }}</button>
            <WhiteSpace />
            <span :title="t('approved', exercise.adaptationStatus.approved)" style="font-size: 130%">✅</span>
          </template>
        </template>
      </template>
    </template>

    <template v-if="exercise.adaptationStatus.kind === 'inProgress'">
      <WhiteSpace />
      <span class="inProgress">({{ t('inProgress') }})</span>
    </template>
  </component>

  <p v-if="context === 'adaptation' || context === 'classification'">
    {{ t('pageAndExercise', { pageNumber: pageNumber ?? 'N/A', exerciseNumber: exerciseNumber ?? 'N/A' }) }}
  </p>
  <p>
    <template v-for="(line, index) in fullTextLines">
      <br v-if="index !== 0" />
      {{ line }}
    </template>
  </p>
  <template v-if="exercise.adaptationStatus.kind !== 'notRequested' && exercise.adaptationStatus.kind !== 'notStarted'">
    <p>
      <button :disabled="exercise.adaptationStatus.kind !== 'success'" @click="rightColumn?.setFullScreen()">
        {{ t('fullScreen') }}
      </button>
    </p>
    <p>
      <RouterLink :to="{ name: 'adaptation', params: { id: exercise.adaptationStatus.id } }">
        <button :disabled="exercise.adaptationStatus.kind === 'inProgress'">
          {{ t('viewDetails') }}
        </button>
      </RouterLink>
    </p>
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
  input: Input
  exercise: Exercise
  classifiedByModel: classified by model
  fixedBy: fixed by
  pageAndExercise: "Page: {pageNumber}, exercise: {exerciseNumber}"
  inProgress: "in progress, will refresh when done"
  fullScreen: Full screen
  viewDetails: View details and make adjustments
  remove: Remove
  approve: Approve
  unapprove: Unapprove
  approved: "Approved by {by}"
fr:
  input: Entrée
  exercise: Exercice
  classifiedByModel: classifié par le modèle
  fixedBy: corrigé par
  pageAndExercise: "Page : {pageNumber}, exercice : {exerciseNumber}"
  inProgress: "en cours, se mettra à jour quand terminé"
  fullScreen: Plein écran
  viewDetails: Voir les détails et faire des ajustements
  remove: Enlever
  approve: Valider
  unapprove: Invalider
  approved: "Validé par {by}"
</i18n>
