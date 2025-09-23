import { loadFixtures, visit, ignoreResizeObserverLoopError } from './utils'

function checkImagesFrontend() {
  cy.get('img').should('have.length', 4)
  cy.get('img')
    .eq(0)
    .should('have.attr', 'src')
    .and(
      'match',
      /^https:\/\/jacquev6\.s3\.amazonaws\.com\/patty\/dev\/extracted-images\/3\.png\?X-Amz-Algorithm=AWS4-HMAC-SHA256/,
    )
  cy.get('img')
    .eq(1)
    .should('have.attr', 'src')
    .and(
      'match',
      /^https:\/\/jacquev6\.s3\.amazonaws\.com\/patty\/dev\/extracted-images\/2\.png\?X-Amz-Algorithm=AWS4-HMAC-SHA256/,
    )
  cy.get('img')
    .eq(2)
    .should('have.attr', 'src')
    .and(
      'match',
      /^https:\/\/jacquev6\.s3\.amazonaws\.com\/patty\/dev\/extracted-images\/1\.png\?X-Amz-Algorithm=AWS4-HMAC-SHA256/,
    )
  cy.get('img').eq(3).should('have.attr', 'src', '/src/adapted-exercise/arrow.png')
}

function checkImagesExport() {
  cy.get('img').should('have.length', 4)
  cy.get('img')
    .eq(0)
    .should('have.attr', 'src')
    .and('match', /^data:image\/png;base64,/)
  cy.get('img')
    .eq(1)
    .should('have.attr', 'src')
    .and('match', /^data:image\/png;base64,/)
  cy.get('img')
    .eq(2)
    .should('have.attr', 'src')
    .and('match', /^data:image\/png;base64,/)
  cy.get('img')
    .eq(3)
    .should('have.attr', 'src')
    .and('match', /^data:image\/png;base64,/)
}

describe('Patty', () => {
  beforeEach(() => {
    ignoreResizeObserverLoopError()
  })

  it('extracts images in sandbox', () => {
    loadFixtures(['seed-data', 'dummy-rcimage-exercise-class'])
    visit('/new-extraction-batch')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/images.pdf')
    cy.get('[data-cy="llm-name"]').eq(0).select('dummy-for-images')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-for-images')
    cy.get('button:contains("Submit")').click()
    cy.contains('in progress').should('exist')
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    cy.get('a:contains("View details")').should('have.attr', 'href', '/adaptation-2')
    checkImagesFrontend()

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })
    cy.get('a:contains("Exercice P1Ex1")').click()
    checkImagesExport()

    cy.visit('/adaptation-2')
    checkImagesFrontend()

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })
    checkImagesExport()
  })

  it('extracts images in textbooks', () => {
    loadFixtures(['seed-data', 'dummy-rcimage-exercise-class', 'dummy-textbook'])
    visit('/textbook-1')
    cy.get('input[type="file"]').eq(0).selectFile('e2e-tests/inputs/images.pdf')
    cy.get('[data-cy="llm-name"]').eq(0).select('dummy-for-images')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-for-images')
    cy.get('button:contains("Submit")').click()
    cy.contains('in progress').should('exist')
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    checkImagesFrontend()

    cy.get('h2').should('have.length', 4)
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 1)
    checkImagesFrontend()

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })
    cy.get('[data-cy="page-number-filter"]').type('1')
    cy.get('a:contains("Exercice 1")').invoke('removeAttr', 'target').click()
    checkImagesExport()
  })
})
