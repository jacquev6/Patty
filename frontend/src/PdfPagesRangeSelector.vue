<script setup lang="ts">
import { type PDFDocumentProxy } from './pdfjs'
import { useI18n } from 'vue-i18n'

import { computedAsync } from '@vueuse/core'
import PdfNavigationControls from './PdfNavigationControls.vue'
import PdfPageRenderer from './PdfPageRenderer.vue'
import { computed, watch } from 'vue'

const props = defineProps<{
  document: PDFDocumentProxy
}>()

const firstPdfPageNumber = defineModel<number>('firstInPdf', { required: true })
const lastPdfPageNumber = defineModel<number>('lastInPdf', { required: true })
const firstTextbookPageNumber = defineModel<number>('firstInTextbook', { required: true })

useI18n()

const firstPdfPageNumberProxy = computed({
  get: () => firstPdfPageNumber.value,
  set: (value) => {
    const increment = value - firstPdfPageNumber.value
    firstPdfPageNumber.value = value
    firstTextbookPageNumber.value += increment
  },
})

const lastTextbookPageNumber = computed(() => {
  return lastPdfPageNumber.value + (firstTextbookPageNumber.value - firstPdfPageNumber.value)
})

watch(firstPdfPageNumber, (newValue) => {
  if (newValue > lastPdfPageNumber.value) {
    lastPdfPageNumber.value = newValue
  }
})

watch(lastPdfPageNumber, (newValue) => {
  if (newValue < firstPdfPageNumberProxy.value) {
    firstPdfPageNumberProxy.value = newValue
  }
})

const firstPage = computedAsync(async () => {
  if (props.document === null) {
    return null
  } else {
    return await props.document.getPage(firstPdfPageNumber.value)
  }
}, null)

const lastPage = computedAsync(async () => {
  if (props.document === null) {
    return null
  } else {
    return await props.document.getPage(lastPdfPageNumber.value)
  }
}, null)
</script>

<template>
  <I18nT keypath="pages" tag="p">
    <template #from>
      <span class="pagePreview">
        <p>
          <PdfNavigationControls v-model:page="firstPdfPageNumberProxy" :pagesCount="document.numPages" /> in pdf
          <i>i.e.</i> <PdfNavigationControls v-model:page="firstTextbookPageNumber" :pagesCount="null" /> in textbook
        </p>
        <PdfPageRenderer v-if="firstPage !== null" :page="firstPage" />
      </span>
    </template>
    <template #to>
      <span class="pagePreview">
        <p>
          <PdfNavigationControls v-model:page="lastPdfPageNumber" :pagesCount="document.numPages" /> in pdf <i>i.e.</i>
          {{ lastTextbookPageNumber }} in textbook
        </p>
        <PdfPageRenderer v-if="lastPage !== null" :page="lastPage" />
      </span>
    </template>
  </I18nT>
</template>

<i18n>
en:
  pages: "Pages: from {from} to {to}"
fr:
  pages: "Pages : de {from} à {to}"
</i18n>

<style scoped>
.pagePreview {
  display: inline-block;
  vertical-align: top;
  width: 35%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.pagePreview > p {
  margin: 0;
}
</style>
