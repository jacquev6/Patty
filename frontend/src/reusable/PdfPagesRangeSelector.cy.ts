import { createI18n } from 'vue-i18n'

import PdfPagesRangeSelector from './PdfPagesRangeSelector.vue'
import pdfjs from '$/pdfjs'
pdfjs.GlobalWorkerOptions.workerSrc = '/__cypress/src/src/frontend/public/pdf.worker.min.js'

function mount() {
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
    })
}

describe('PdfPagesRangeSelector', () => {
  it('has correct initial values', () => {
    mount()
    cy.get('input').should('have.length', 3)
    cy.get('input').eq(0).should('have.value', '1')
    cy.get('input').eq(1).should('have.value', '1')
    cy.get('input').eq(2).should('have.value', '35')
    cy.get(':contains("35 in textbook")').should('exist')
  })

  it('reduces first page when setting last page too low - in the text input', () => {
    mount()
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

  it('reduces first page when setting last page too low - with the arrow buttons', () => {
    mount()
    cy.get('input').eq(0).clear().type('8')
    cy.get('input').eq(2).clear().type('8')
    cy.get('button').eq(4).click() // Decrease last page
    cy.get('input').eq(2).should('have.value', '7')
    cy.get('input').eq(0).should('have.value', '7')
  })

  it('increases last page when setting first page too high - in the text input', () => {
    mount()
    cy.get('input').eq(2).clear()
    cy.get(':contains("35 in textbook")').should('exist') // Not updated by clear
    cy.get('input').eq(2).type('5')
    cy.get(':contains("5 in textbook")').should('exist') // Updated before blur
    cy.get('input').eq(0).clear()
    cy.get('input').eq(1).should('have.value', '1') // Not updated by clear
    cy.get('input').eq(0).type('8')
    cy.get('input').eq(1).should('have.value', '8') // Updated before blur: required to display the right page
    cy.get('input').eq(2).should('have.value', '5') // Not fixed before blur
    cy.get('input').eq(0).blur()
    cy.get('input').eq(2).should('have.value', '8')
  })

  it('increases last page when setting first page too high - with the arrow buttons', () => {
    mount()
    cy.get('input').eq(0).clear().type('8')
    cy.get('input').eq(2).clear().type('8')
    cy.get('button').eq(1).click() // Increase first page
    cy.get('input').eq(0).should('have.value', '9')
    cy.get('input').eq(2).should('have.value', '9')
  })

  it('reproduces issue 132', () => {
    mount()
    cy.get('input').eq(0).clear().type('10')
    cy.get('input').eq(2).clear().type('25').blur()
    cy.get('input').eq(0).should('have.value', '10')
  })
})
