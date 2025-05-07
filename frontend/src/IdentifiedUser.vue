<script setup lang="ts">
import { ref } from 'vue'

import WhiteSpace from './WhiteSpace.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const identifiedUser = useIdentifiedUserStore()

const showEditor = ref(identifiedUser.identifier === '')
</script>

<template>
  <span
    >{{ identifiedUser.identifier }}
    <span data-cy="edit-identified-user" class="edit" @click="showEditor = true">(🖊️ change)</span></span
  >
  <Teleport to="body" v-if="showEditor">
    <div class="editor">
      <div>
        <h1>Identification</h1>
        <p>
          Your first name:
          <input data-cy="identified-user" v-model="identifiedUser.identifier" />
          <WhiteSpace />
          <button data-cy="identified-user-ok" @click="showEditor = false" :disabled="identifiedUser.identifier === ''">
            OK
          </button>
        </p>
        <p>(Nothing is checked, this is used only to record who created what.)</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.edit {
  cursor: pointer;
  font-size: small;
  color: grey;
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
