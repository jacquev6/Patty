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

  it('creates a textbook with only a title, and with an adaptation batch', () => {
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="textbook-title"]').type('Dummy title', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.enabled').click()

    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1').should('have.text', 'Dummy title')
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="strategy-settings"]').should('have.value', '-- choose --').select('Branchy McBranchFace')
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="input-page-number"]').type('42', { delay: 0 })
    cy.get('[data-cy="input-exercise-number"]').type('4', { delay: 0 })
    cy.get('[data-cy="input-text"]').type('Dummy input text', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.get('[data-cy="strategy-settings"]').should('have.value', '-- choose --')
    cy.get('[data-cy="input-text"]').should('have.length', 1).should('have.value', '')
    cy.get('button:contains("Submit")').should('be.disabled')

    cy.get('h3:contains("Branchy McBranchFace")').should('exist')
    cy.get('h4:contains("input 1")').should('exist')

    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2:contains("Page 42")').should('exist')

    cy.visit('/')
    cy.get('li:contains("Dummy title")').should('exist').should('contain', 'Dummy title (created by Alice on')
  })

  it('creates a textbook with all fields', () => {
    cy.get('[data-cy="textbook-title"]').type('The title', { delay: 0 })
    cy.get('[data-cy="textbook-editor"]').type('Dummy editor', { delay: 0 })
    cy.get('[data-cy="textbook-year"]').type('2023', { delay: 0 })
    cy.get('[data-cy="textbook-isbn"]').type('978-3-16-148410-0', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1').should('have.text', 'The title, Dummy editor, 2023 (ISBN: 978-3-16-148410-0)')

    cy.visit('/')
    cy.get('li:contains("The title")')
      .should('exist')
      .should('contain', 'The title, Dummy editor, 2023 (created by Alice on')
  })
})

describe('The edition form for textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('looks like this - by batch', () => {
    screenshot('textbook-edition-form-by-batch')
  })

  it('looks like this - by page', () => {
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('p:contains("sorted by page")').should('exist')
    cy.get('h2').should('have.length', 2)
    cy.get('h3').should('have.length', 6)
    cy.get('h2').eq(0).should('have.text', 'Page 40')
    cy.get('h3').eq(0).should('have.text', 'Exercise 4')
    cy.get('h3').eq(1).should('have.text', 'Exercise 6')
    cy.get('h3').eq(2).should('have.text', 'Exercise 8')
    cy.get('h3').eq(3).should('have.text', 'Exercise 30')
    cy.get('h2').eq(1).should('have.text', 'Page 42')
    cy.get('h3').eq(4).should('have.text', 'Exercise 5')
    cy.get('h3').eq(5).should('have.text', 'Exercise 6')
    screenshot('textbook-edition-form-by-page')
  })

  it('removes and re-adds batches and exercises', () => {
    cy.get('button:contains("Full screen")').should('have.length', 8)
    cy.get('h3').eq(1).find('button:contains("Remove")').click()
    cy.get('button:contains("Full screen")').should('have.length', 5)
    cy.get('h3').eq(2).find('button:contains("Remove")').click()
    cy.get('button:contains("Full screen")').should('have.length', 2)
    cy.get('h3').eq(3).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 3)
    cy.get('h3').eq(1).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 6)
    cy.get('h3').eq(2).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 9)

    cy.get('h4').eq(0).find('button:contains("Remove")').click()
    cy.get('button:contains("Full screen")').should('have.length', 8)
    cy.get('h4').eq(1).find('button:contains("Remove")').click()
    cy.get('button:contains("Full screen")').should('have.length', 7)
    cy.get('h4').eq(2).find('button:contains("Remove")').click()
    cy.get('button:contains("Full screen")').should('have.length', 6)
    cy.get('h4').eq(0).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 7)
    cy.get('h4').eq(1).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 8)
    cy.get('h4').eq(2).find('button:contains("Re-add")').click()
    cy.get('button:contains("Full screen")').should('have.length', 9)
  })
})
