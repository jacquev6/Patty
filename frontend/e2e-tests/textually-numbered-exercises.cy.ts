import { ignoreResizeObserverLoopError, visit, loadFixtures } from './utils'

describe('Adaptation batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-adaptation'])
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-adaptation-batch')
    cy.get('[data-cy="input-exercise-number"]').eq(0).clear().type('5')
    cy.get('[data-cy="input-page-number"]').eq(1).type('42')
    cy.get('[data-cy="input-exercise-number"]').eq(1).type('Not a number')
    cy.get('[data-cy="input-text"]').eq(1).type('Blah')
    cy.get('[data-cy="input-page-number"]').eq(2).type('42')
    cy.get('[data-cy="input-exercise-number"]').eq(2).type('6')
    cy.get('[data-cy="input-text"]').eq(2).type('Bar baz')
    cy.get('button:contains("Submit")').click()
    cy.get('h2 + p:contains("Page:")').should('have.length', 3)
    // Inputs order is preserved
    cy.get('h2 + p:contains("Page:")').eq(0).should('have.text', 'Page: 42, exercise: 5')
    cy.get('h2 + p:contains("Page:")').eq(1).should('have.text', 'Page: 42, exercise: Not a number')
    cy.get('h2 + p:contains("Page:")').eq(2).should('have.text', 'Page: 42, exercise: 6')
  })
})

describe('Classification batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-classification-batch')
    cy.get('[data-cy="input-exercise-number"]').eq(0).type('5')
    cy.get('[data-cy="input-page-number"]').eq(0).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(0).type('Instruction 5')
    cy.get('[data-cy="input-statement-text"]').eq(0).type('Statement 5')
    cy.get('[data-cy="input-exercise-number"]').eq(1).type('Not a number')
    cy.get('[data-cy="input-page-number"]').eq(1).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(1).type('Instruction Not a number')
    cy.get('[data-cy="input-statement-text"]').eq(1).type('Statement Not a number')
    cy.get('[data-cy="input-exercise-number"]').eq(2).type('6')
    cy.get('[data-cy="input-page-number"]').eq(2).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(2).type('Instruction 6')
    cy.get('[data-cy="input-statement-text"]').eq(2).type('Statement 6')
    cy.get('button:contains("Submit")').click()
    cy.get('h2 + p:contains("Page:")').should('have.length', 3)
    // Inputs order is preserved
    cy.get('h2 + p:contains("Page:")').eq(0).should('have.text', 'Page: 42, exercise: 5')
    cy.get('h2 + p:contains("Page:")').eq(1).should('have.text', 'Page: 42, exercise: Not a number')
    cy.get('h2 + p:contains("Page:")').eq(2).should('have.text', 'Page: 42, exercise: 6')
  })
})

describe('Extraction batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-extraction-strategy'])
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-extraction-batch')
    cy.get('select').eq(2).select('dummy-for-textually-numbered-exercises')
    cy.get('select').eq(3).select('no')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('input[type="number"]').eq(1).clear().type('1')
    cy.get('button:contains("Submit")').click()
    cy.get('h3').should('have.length', 5)
    cy.get('h3').eq(2).should('have.text', 'Exercise 5')
    cy.get('h3').eq(3).should('have.text', 'Not a number')
    cy.get('h3').eq(4).should('have.text', 'Exercise 6')
  })
})

describe('Textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-extraction-strategy'])
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-textbook')
    cy.get('[data-cy="textbook-title"]').type('Title')
    cy.get('label:contains("Single PDF") input').check()
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('label:contains("1-2") input').check()
    cy.get('select').eq(2).select('dummy-for-textually-numbered-exercises')
    cy.get('button:contains("Submit")').click()
    cy.get('li a:contains("1")').click()
    cy.get('h2').should('have.length', 3)
    cy.get('h2').eq(0).should('contain', 'Exercise 5')
    cy.get('h2').eq(1).should('contain', 'Not a number')
    cy.get('h2').eq(2).should('contain', 'Exercise 6')
  })
})
