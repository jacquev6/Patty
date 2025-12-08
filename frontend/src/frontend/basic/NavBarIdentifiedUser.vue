<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import WhiteSpace from '$/WhiteSpace.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const identifiedUser = useIdentifiedUserStore()
const { t } = useI18n()

const showEditor = ref(identifiedUser.identifier === '')
</script>

<template>
  <span data-cy="edit-identified-user" @click="showEditor = true" class="edit">
    👤 {{ identifiedUser.identifier }}
  </span>
  <Teleport to="body" v-if="showEditor">
    <div class="editor">
      <div>
        <h1>{{ t('identification') }}</h1>
        <p>
          {{ t('firstName') }}
          <input data-cy="identified-user" v-model="identifiedUser.identifier" />
          <WhiteSpace />
          <button data-cy="identified-user-ok" @click="showEditor = false" :disabled="identifiedUser.identifier === ''">
            {{ t('ok') }}
          </button>
        </p>
        <p>({{ t('message') }})</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.edit {
  cursor: pointer;
}

.editor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
}

.editor > div {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
}
</style>

<i18n>
en:
  identification: Identification
  firstName: "Your first name:"
  ok: OK
  message: "Nothing is checked, this is used only to record who created what."
fr:
  identification: Identification
  firstName: "Votre prénom :"
  ok: OK
  message: "Rien n'est vérifié, ceci sert uniquement à enregistrer qui a créé quoi."
</i18n>
