<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { ref } from 'vue'

import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import TriColoredInput from './TriColoredInput.vue'

const model = ref('')
</script>

<template>
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <p>
    TriColoredInput: <TriColoredInput :digitsOnly="true" v-model="model" /> <span>{{ model }}</span>
  </p>
  <p><VirtualNumericalKeyboard /></p>
</template>
