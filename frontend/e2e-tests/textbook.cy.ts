import { ignoreResizeObserverLoopError, loadFixtures, screenshot, visit } from './utils'

describe('The creation form for textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-branch'])
    ignoreResizeObserverLoopError()
    visit('/')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('creates a textbook with only a title', () => {
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="textbook-title"]').type('Dummy title', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.enabled').click()

    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1').should('have.text', 'Dummy title')

    cy.visit('/')
    cy.get('li:contains("Dummy title")').should('exist').should('contain', 'Dummy title (created by Alice on')
  })

  it('creates a textbook with all fields', () => {
    cy.get('[data-cy="textbook-title"]').type('The title', { delay: 0 })
    cy.get('[data-cy="textbook-publisher"]').type('Dummy publisher', { delay: 0 })
    cy.get('[data-cy="textbook-year"]').type('2023', { delay: 0 })
    cy.get('[data-cy="textbook-isbn"]').type('978-3-16-148410-0', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1').should('have.text', 'The title, Dummy publisher, 2023 (ISBN: 978-3-16-148410-0)')

    cy.visit('/')
    cy.get('li:contains("The title")')
      .should('exist')
      .should('contain', 'The title, Dummy publisher, 2023 (created by Alice on')
  })
})

describe('The edition form for textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
  })

  it('looks like this - by batch', () => {
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('p:contains("in creation order")').should('exist')
    screenshot('textbook-edition-form-by-batch')
  })

  it('looks like this - by page', () => {
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('p:contains("sorted by page")').should('exist')
    screenshot('textbook-edition-form-by-page')
  })

  it('adds and removes external exercises', () => {
    cy.get("input[data-cy='external-files']").selectFile([
      'e2e-tests/inputs/P40Ex1.docx',
      'e2e-tests/inputs/P40Ex7.docx',
    ])
    cy.get('.busy').should('not.exist')

    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.text', 'Page 40')
    cy.get('h2').should('have.length', 1)
    cy.get('h3').should('have.length', 2)
    cy.get('h3').eq(0).should('have.text', 'Exercise 1')
    cy.get('h3').eq(1).should('have.text', 'Exercise 7')

    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('button:contains("Remove")').eq(0).click()

    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.text', 'Page 40')
    cy.get('h2').should('have.length', 1)
    cy.get('h3').should('have.length', 1)
    cy.get('h3').eq(0).should('have.text', 'Exercise 7')

    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Remove")').should('have.length', 1)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Re-add")').should('have.length', 2)
    cy.get('button:contains("Re-add")').eq(0).click()

    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.text', 'Page 40')
    cy.get('h2').should('have.length', 1)
    cy.get('h3').should('have.length', 1)
    cy.get('h3').eq(0).should('have.text', 'Exercise 1')
  })
})
