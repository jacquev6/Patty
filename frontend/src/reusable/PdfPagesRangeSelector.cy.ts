import { createI18n } from 'vue-i18n'

import PdfPagesRangeSelector from './PdfPagesRangeSelector.vue'
import pdfjs from '$/pdfjs'
pdfjs.GlobalWorkerOptions.workerSrc = '/__cypress/src/src/frontend/public/pdf.worker.min.js'

function mountThen(f: () => void) {
  cy.wrap(null)
    .then(() => pdfjs.getDocument('e2e-tests/inputs/long.pdf').promise)
    .then((document) => {
      // Weirdly, the page previews are not rendered.
      // But it is not required for this test, so I did not spend too much time trying to fix that.
      expect(document.numPages).to.equal(35)
      cy.mount(PdfPagesRangeSelector, {
        props: {
          document,
          firstInPdf: 1,
          lastInPdf: document.numPages,
          firstInTextbook: 1,
        },
        global: {
          plugins: [createI18n({ legacy: false, locale: 'en', fallbackLocale: 'en' })],
        },
      })
      f()
    })
}

describe('PdfPagesRangeSelector', () => {
  it('has correct initial values', () => {
    mountThen(() => {
      cy.get('input').should('have.length', 3)
      cy.get('input').eq(0).should('have.value', '1')
      cy.get('input').eq(1).should('have.value', '1')
      cy.get('input').eq(2).should('have.value', '35')
      cy.get(':contains("35 in textbook")').should('exist')
    })
  })

  it('reduces first page when setting last page too low', () => {
    mountThen(() => {
      cy.get('input').eq(0).clear()
      cy.get('input').eq(1).should('have.value', '1') // Not updated by clear
      cy.get('input').eq(0).type('8')
      cy.get('input').eq(1).should('have.value', '8') // Updated before blur: required to display the right page
      cy.get('input').eq(0).blur()
      cy.get(':contains("35 in textbook")').should('exist')
      cy.get('input').eq(2).clear()
      cy.get(':contains("35 in textbook")').should('exist') // Not updated by clear
      cy.get('input').eq(2).type('5')
      cy.get(':contains("5 in textbook")').should('exist') // Updated before blur
      cy.get('input').eq(0).should('have.value', '8') // Not fixed before blur
      cy.get('input').eq(2).blur()
      cy.get('input').eq(0).should('have.value', '5')
    })
  })

  it('increases last page when setting first page too high', () => {
    mountThen(() => {
      cy.get('input').eq(2).clear().type('5')
      cy.get('input').eq(0).clear().type('8').blur()
      cy.get('input').eq(2).should('have.value', '8')
    })
  })

  it('reproduces issue 132', () => {
    mountThen(() => {
      cy.get('input').eq(0).clear().type('10')
      cy.get('input').eq(2).clear().type('25').blur()
      cy.get('input').eq(0).should('have.value', '10')
    })
  })
})
