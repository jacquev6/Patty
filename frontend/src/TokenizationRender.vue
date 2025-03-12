<script setup lang="ts">
import type { Tokenization } from './apiClient'

const props = defineProps<{
  tokenizedText: Tokenization['steps'][number]['tokenized_text']
}>()
</script>

<template>
  <p v-for="sentence in props.tokenizedText.sentences" class="sentence">
    <template v-for="token in sentence.tokens">
      <span v-if="token.kind == 'word'" class="word" :title="JSON.stringify(token)">{{ token.text }}</span>
      <span v-else-if="token.kind == 'punctuation'" class="punctuation" :title="JSON.stringify(token)">{{
        token.text
      }}</span>
      <span v-else>BUG: {{ ((token: never) => token)(token) }}</span>
    </template>
  </p>
</template>

<style scoped>
span {
  margin-right: 0.5em;
}

.word {
  background-color: yellow;
}

.punctuation {
  background-color: #66f;
}
</style>
