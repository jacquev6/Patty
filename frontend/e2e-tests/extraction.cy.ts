import { ignoreResizeObserverLoopError, loadFixtures, visit, screenshot } from './utils'

describe('The extraction batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-adaptation', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/new-extraction-batch')
  })

  it('looks like this', () => {
    screenshot('extraction-batch-creation-page')
  })

  it('looks like this after selecting a PDF', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('p:contains("PDF file:")').should('contain.text', '(uploaded)', { timeout: 10000 })
    cy.get('div.busy').should('not.exist')
    screenshot('extraction-batch-creation-page-with-pdf')
  })

  it('creates an extraction batch without classification or adaptation, then requests them and refreshes until they are done', () => {
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('p:contains("PDF file:")').should('contain.text', '(uploading...)')
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('p:contains("PDF file:")', { timeout: 10000 }).should('contain.text', '(uploaded)')
    cy.get('canvas[data-cy-rendered-page="1"]').should('exist')
    cy.get('canvas[data-cy-rendered-page="2"]').should('exist')
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('eq', '/extraction-batch-1')
    cy.get('h2 span.inProgress:contains("in progress")').should('exist')
    cy.get('h2 span.inProgress:contains("in progress")', { timeout: 10000 }).should('not.exist')
    cy.get('h2:contains("Page")').should('have.length', 2)
    cy.get('h3:contains("Exercise")').should('have.length', 4)
    cy.get('.inProgress').should('not.exist')
    cy.get('p:contains("Run classification after extraction: no")').should('exist')
    cy.get('p:contains("Run adaptations")').should('not.exist')
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.get('span:contains("(🖊️ change)")').click()
    cy.get('button:contains("Submit")').click()
    cy.get('h3 span.inProgress:contains("in progress")').should('have.length', 4)
    cy.get('h3 span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('h3 span.inProgress:contains("in progress")').should('not.exist')
    cy.get('p:contains("Adaptation was not requested.")').should('exist')

    cy.get('span:contains("(🖊️ change)")').click()
    cy.get('button:contains("Submit")').click()
    cy.get('div.busy').should('exist')
    cy.get('div.busy').should('not.exist')
    cy.get('p:contains("Adaptation was not requested.")').should('not.exist')
  })

  it('creates an extraction batch with classification and adaptation, refreshes it until it is done, then creates settings for the unknown class, then requests the adaptation and refreshes until it is done', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-3')
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('eq', '/extraction-batch-1')
    cy.get('h2 span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('h2 span.inProgress:contains("in progress")').should('have.length', 1)
    cy.get('h2 span.inProgress:contains("in progress")').should('not.exist')
    cy.get('h3 span.inProgress:contains("in progress")').should('have.length', 4)
    cy.get('div.busy').should('have.length', 2)
    cy.get('h3 span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('div.busy', { timeout: 10000 }).should('not.exist')
    cy.get('h3 span.inProgress:contains("in progress")').should('not.exist')
    cy.get('p:contains("Exercise class VraiFaux does not have adaptation settings yet.")').should('exist')
    cy.get('button:contains("Full screen")').should('have.length', 2)

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="settings-name"]').type('VraiFaux', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('div.busy').should('not.exist')

    cy.visit('/extraction-batch-1')
    cy.get(
      'p:contains("Exercise class VraiFaux did not have adaptation settings when this exercise was created.")',
    ).should('exist')
    cy.get('button:contains("Submit all adaptations in the same case")').first().click()
    cy.get('div.busy').should('have.length', 2)
    cy.get('div.busy', { timeout: 10000 }).should('not.exist')

    cy.visit('/extraction-batch-1')
    cy.get('p:contains("Created by: Alice")').should('exist')
    screenshot('extraction-batch-edition-page')

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        expect(href).to.include('/api/export/sandbox-extraction-batch-1.html?token=')
        cy.visit(`${href}&download=false`)
      })
    cy.get('a:contains("Exercice")').should('have.length', 4)

    cy.visit('/')
    cy.get('ul:contains("Batch E1 (created by Alice")').should('exist')
    cy.get('a:contains("Batch E1")').should('have.attr', 'href', '/extraction-batch-1')
    cy.get('ul:contains("Batch C")').should('not.exist')

    cy.visit('/adaptation-2')
    cy.get('a:contains("Extraction batch 1")').should('have.attr', 'href', '/extraction-batch-1')
  })

  it('remembers the last strategy used', () => {
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('[data-cy="llm-name"]').should('have.length', 1)
    cy.get('[data-cy="llm-name"]').should('have.value', 'dummy-1').select('dummy-2')
    cy.get('[data-cy="prompt"]')
      .should('have.value', 'Blah blah blah.')
      .type('{selectAll}Bleh bleh.')
      .should('have.value', 'Bleh bleh.')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('button:contains("Submit")').click()
    cy.get('.inProgress').should('exist')
    cy.get('.inProgress').should('not.exist')
    cy.get('p:contains("Provider: dummy, model: dummy-2")').should('exist')
    cy.get('p:contains("Bleh bleh.")').should('exist')

    cy.visit('/new-extraction-batch')
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('[data-cy="llm-name"]').should('have.length', 1)
    cy.get('[data-cy="llm-name"]').should('have.value', 'dummy-1') // Model is not remembered
    cy.get('[data-cy="prompt"]').should('have.value', 'Bleh bleh.')
  })

  it('handles non-JSON response from the LLM', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('[data-cy="prompt"]').type('{selectAll}Not JSON')
    cy.get('input[type="number"]').eq(1).type('{selectAll}1')
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("The LLM returned a response that is not correct JSON.")').should('exist')
  })

  it('handles invalid JSON response from the LLM', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('[data-cy="prompt"]').type('{selectAll}Invalid JSON')
    cy.get('input[type="number"]').eq(1).type('{selectAll}1')
    cy.get('button:contains("Submit")').click()
    cy.get(
      'p:contains("The LLM returned a JSON response that does not validate against the extracted exercises list schema.")',
    ).should('exist')
  })

  it('handles unknown error from the LLM', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('[data-cy="run-classification"]').select('no')
    cy.get('[data-cy="prompt"]').type('{selectAll}Unknown error')
    cy.get('input[type="number"]').eq(1).type('{selectAll}1')
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("The LLM caused an unknown error.")').should('exist')
  })
})
