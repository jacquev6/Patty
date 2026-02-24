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
import { type PDFDocumentProxy } from '../../reusable/pdfjs'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { computedAsync } from '@vueuse/core'

import PdfNavigationControls from '$/PdfNavigationControls.vue'
import PdfPageRenderer from '$/PdfPageRenderer.vue'
import WhiteSpace from '@/reusable/WhiteSpace.vue'

const props = defineProps<{
  document: PDFDocumentProxy
  pdfToTextbookPageNumbersFixedDelta: number | null
}>()

const pdfPageNumber = defineModel<number>('pdfPageNumber', { required: true })
const textbookPageNumber = defineModel<number>('textbookPageNumber', { required: true })

useI18n()

const pdfPageNumberProxy = computed({
  get: () => pdfPageNumber.value,
  set: (value) => {
    const delta = props.pdfToTextbookPageNumbersFixedDelta ?? textbookPageNumber.value - pdfPageNumber.value
    pdfPageNumber.value = value
    textbookPageNumber.value = value + delta
  },
})

const page = computedAsync(() => props.document.getPage(pdfPageNumber.value), null)
</script>

<template>
  <span class="pagePreview">
    <p>
      <slot name="label"></slot>
      <WhiteSpace />
      <I18nT keypath="inPdfIeInTextbook">
        <template #pdfPage>
          <PdfNavigationControls v-model="pdfPageNumberProxy" :pagesCount="document.numPages" />
        </template>
        <template #textbookPage>
          <template v-if="props.pdfToTextbookPageNumbersFixedDelta === null">
            <PdfNavigationControls v-model="textbookPageNumber" :pagesCount="null" />
          </template>
          <template v-else>
            {{ textbookPageNumber }}
          </template>
        </template>
      </I18nT>
    </p>
    <PdfPageRenderer v-if="page !== null" :page />
  </span>
</template>

<i18n>
en:
  inPdfIeInTextbook: "page {pdfPage} in pdf is page {textbookPage} in textbook"
fr:
  inPdfIeInTextbook: "la page {pdfPage} dans le pdf est la page {textbookPage} dans le manuel"
</i18n>

<style scoped>
.pagePreview {
  display: inline-block;
  vertical-align: top;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.pagePreview > p {
  margin: 0;
}
</style>
