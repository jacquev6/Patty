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
import type { ImageRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import ImageRenderer from '@/adapted-exercise/components/ImageRenderer.vue'

const props = defineProps<{
  component: ImageRenderable
}>()
</script>

<template>
  <p :style="{ textAlign: props.component.align }"><ImageRenderer :url="component.url" :height="component.height" /></p>
</template>
