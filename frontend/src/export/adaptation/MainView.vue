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
import type { AdaptedExercise, ImagesUrls } from '@/frontend/ApiClient'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'

// WARNING: changing this type requires changing the export code in the backend
type Data = {
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
  imagesUrls: ImagesUrls
}

const data = JSON.parse('##TO_BE_SUBSTITUTED_ADAPTATION_EXPORT_DATA##') as Data
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="data" style="height: 100vh" />
</template>
