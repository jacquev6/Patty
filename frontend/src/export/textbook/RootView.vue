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
import { provideDisplayPreferences } from './displayPreferences'

// WARNING: changing these types requires changing the export code in the backend
export type Exercise =
  | {
      exerciseId: string
      pageNumber: number
      exerciseNumber: string
      kind: 'adapted'
      studentAnswersStorageKey: string
      adaptedExercise: AdaptedExercise
      imagesUrls: ImagesUrls
    }
  | {
      exerciseId: string
      pageNumber: number
      exerciseNumber: string
      kind: 'external'
      originalFileName: string
      data: string
    }

export type Lesson = {
  kind: 'lesson'
  pageNumber: number
  originalFileName: string
  data: string
}

export type Data = {
  title: string
  lessons: Lesson[]
  exercises: Exercise[]
}

const data = JSON.parse('##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##') as Data

provideDisplayPreferences()
</script>

<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" :data />
  </RouterView>
</template>
