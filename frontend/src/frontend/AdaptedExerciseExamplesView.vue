<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->
  
<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

import { examples } from './AdaptedExerciseExamples.ts'
import { defaultSpacingVariables } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import ExamplesViewExercise from './AdaptedExerciseExamplesViewExercise.vue'
import { useBreadcrumbsStore } from './basic/BreadcrumbsStore'

const breadcrumbsStore = useBreadcrumbsStore()
const { t } = useI18n()

const spacingVariables = reactive(defaultSpacingVariables())

onMounted(() => {
  breadcrumbsStore.set([{ textKey: 'sandbox' }, { textKey: 'adaptedExerciseExamples', to: {} }])
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <h1>{{ t('spacing') }}</h1>
    <p>{{ t('changesNotSaved') }}</p>
    <dl>
      <template v-for="(variable, key) in spacingVariables" :key="key">
        <dt>
          <b>{{ key }}</b>
        </dt>
        <dd>
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-v-html -->
          <span v-html="t(`variable.${key}`)"></span> :
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          <input type="number" v-model="spacingVariables[key]" />em
        </dd>
      </template>
    </dl>

    <h1>{{ t('examples') }}</h1>
    <template v-for="example in examples" :key="example.title">
      <div style="margin-bottom: 10px">
        <ExamplesViewExercise :example :spacingVariables />
      </div>
    </template>
  </div>
</template>

<i18n>
en:
  spacing: Spacing and sizes
  changesNotSaved: Changes made here are not saved, and applied only on this page, temporarily.
  variable:
    '--extra-horizontal-space-between-words': 'Added to the standard horizontal space between words'
    '--optional-extra-horizontal-space-between-letters-in-editable-text-input': 'Horizontal space added between letters when a <code>"kind": "editableTextInput" has <code>"increaseHorizontalSpace" : true</code></code>'
    '--font-size-for-single-character-selectable': 'Font size when a <code>"kind": "selectableInput"</code> contains a single character and is stuck to another <code>"kind": "selectableInput"</code>'
    '--extra-horizontal-space-around-single-letter-selectable': 'Space added left and right of that single character when it is a letter'
    '--extra-vertical-space-around-single-letter-selectable': 'Space added above and below that letter'
    '--extra-horizontal-space-around-single-punctuation-selectable': 'Space added left and right of that single character when it is a punctuation mark'
    '--extra-vertical-space-around-single-punctuation-selectable': 'Space added above and below that punctuation mark'
    '--vertical-space-between-top-and-instruction': 'Vertical space between the top of the page and the instruction'
    '--vertical-space-between-instruction-lines': 'Vertical space between lines in the instruction'
    '--vertical-space-between-instruction-and-statement': 'Vertical space between the instruction and the statement'
    '--vertical-space-between-statement-lines': 'Vertical space between lines in the statement'
    '--vertical-space-between-border-and-choices': 'Vertical space between the border and choices in a <code>"kind": "multipleChoicesInput"</code>'
    '--vertical-space-between-choices-lines': 'Vertical space between lines in the choices of a <code>"kind": "multipleChoicesInput"</code>'
    '--clickable-padding-around-next-page-arrow': 'Vertical and horizontal space that can be clicked around the "next page" arrow'
  examples: Examples
fr:
  spacing: Espacement et dimensions
  changesNotSaved: Les modifications effectuées ici ne sont pas enregistrées, et ne s'appliquent qu'à cette page, temporairement.
  variable:
    '--extra-horizontal-space-between-words': 'Ajouté à l’espace horizontal standard entre les mots'
    '--optional-extra-horizontal-space-between-letters-in-editable-text-input': 'Espace horizontal ajouté entre les lettres quand un <code>"kind": "editableTextInput"</code> a <code>"increaseHorizontalSpace" : true</code>'
    '--font-size-for-single-character-selectable': 'Taille de police quand un <code>"kind": "selectableInput"</code> contient un seul caractère et est collé à un autre <code>"kind": "selectableInput"</code>'
    '--extra-horizontal-space-around-single-letter-selectable': 'Espace ajouté à gauche et à droite de cet unique caractère quand il s’agit d’une lettre'
    '--extra-vertical-space-around-single-letter-selectable': 'Espace ajouté au dessus et en dessous de cette lettre'
    '--extra-horizontal-space-around-single-punctuation-selectable': 'Espace ajouté à gauche et à droite de cet unique caractère quand il s’agit d’un signe de ponctuation'
    '--extra-vertical-space-around-single-punctuation-selectable': 'Espace ajouté au dessus et en dessous de ce signe de ponctuation'
    '--vertical-space-between-top-and-instruction': 'Espace vertical entre le haut de la page et l’instruction'
    '--vertical-space-between-instruction-lines': 'Espace vertical entre les lignes de l’instruction'
    '--vertical-space-between-instruction-and-statement': 'Espace vertical entre l’instruction et l’énoncé'
    '--vertical-space-between-statement-lines': 'Espace vertical entre les lignes de l’énoncé'
    '--vertical-space-between-border-and-choices': 'Espace vertical entre le cadre et les choix dans un <code>"kind": "multipleChoicesInput"</code>'
    '--vertical-space-between-choices-lines': 'Espace vertical entre les lignes des choix dans un <code>"kind": "multipleChoicesInput"</code>'
    '--clickable-padding-around-next-page-arrow': 'Espace vertical et horizontal cliquable autour de la flèche "page suivante"'
  examples: Exemples
</i18n>
