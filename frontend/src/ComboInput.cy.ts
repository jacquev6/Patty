import ComboInput from './ComboInput.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
  screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
  const name = `${baseName}-${screenshotsCounts[baseName]}-${Cypress.browser.name}`
  cy.compareSnapshot(name)
}

describe('ComboInput', () => {
  it('puts additional attributes on the input', () => {
    cy.mount(ComboInput, {
      props: { modelValue: '', suggestions: [], maxSuggestionsDisplayCount: 4 },
      attrs: { 'data-foo': 'bar' },
    })

    cy.get('input').should('have.attr', 'data-foo', 'bar')
  })

  it('renders', () => {
    cy.mount(ComboInput, {
      props: {
        modelValue: '',
        suggestions: ['Alpha 1', 'Alpha 2', 'Bravo', 'Charlie'],
        maxSuggestionsDisplayCount: 4,
      },
    })

    cy.get('span.clue').should('exist')
    cy.get('div.suggestions').should('not.exist')
    screenshot()
    cy.get('input').focus()
    cy.get('span.clue').should('not.exist')
    cy.get('div.suggestions').should('exist')
    screenshot()
    cy.get('div.suggestions > p').eq(2).click()
    cy.get('input').should('have.value', 'Bravo')
    cy.get('div.suggestions').should('not.exist')
    cy.get('span.clue').should('exist')
    screenshot()
  })

  it('renders with many suggestions', () => {
    cy.mount(ComboInput, {
      props: {
        modelValue: '',
        suggestions: Array.from({ length: 10 }, (_, i) => `Suggestion ${i}`),
        maxSuggestionsDisplayCount: 5,
      },
    })

    cy.get('input').focus()
    cy.get('div.suggestions > p.suggestion').should('have.length', 5)
    cy.get('div.suggestions > p').should('have.length', 6)
    screenshot()
  })

  it('filters suggestions', () => {
    cy.mount(ComboInput, {
      props: {
        modelValue: '',
        suggestions: ['Alpha 1', 'Alpha 2', 'Bravo', 'Charlie'],
        maxSuggestionsDisplayCount: 4,
      },
    })

    cy.get('input').focus()
    cy.get('div.suggestions > p.suggestion').should('have.length', 4)
    cy.get('input').type('h')
    cy.get('div.suggestions > p.suggestion').should('have.length', 3)
    cy.get('input').type('ar')
    cy.get('div.suggestions > p.suggestion').should('have.length', 1)
  })
})
