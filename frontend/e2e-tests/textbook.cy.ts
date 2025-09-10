import { ignoreResizeObserverLoopError, loadFixtures, screenshot, visit } from './utils'

describe('The creation form for textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-branch'])
    ignoreResizeObserverLoopError()
    visit('/')
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

describe('The edition form for textbooks - empty', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
  })

  function screenshots(slug: string) {
    cy.get('[data-cy="view-by"]').select('page').blur()
    cy.get('p:contains("sorted by page")').should('exist')
    cy.get('div.main').scrollTo('top', { ensureScrollable: false })
    screenshot(`${slug}-edition-form-by-page`)
    cy.get('[data-cy="view-by"]').select('batch').blur()
    cy.get('p:contains("in creation order")').should('exist')
    cy.get('div.main').scrollTo('top', { ensureScrollable: false })
    screenshot(`${slug}-edition-form-by-batch`)
  }

  it('adds and removes PDF ranges', () => {
    screenshots('empty-textbook')

    cy.get('input[type="file"]').eq(0).selectFile('e2e-tests/inputs/test.pdf')
    cy.get('p:contains("i.e. 2 in textbook")').should('exist')
    cy.get('input[type="number"]').eq(1).type('{selectAll}6')
    cy.get('p:contains("i.e. 7 in textbook")').should('exist')
    cy.get('[data-cy="extraction"] [data-cy="llm-provider"]').select('dummy')
    cy.get('[data-cy="extraction"] [data-cy="llm-name"]').select('dummy-1')
    cy.get('[data-cy="adaptation"] [data-cy="llm-provider"]').select('dummy')
    cy.get('[data-cy="adaptation"] [data-cy="llm-name"]').select('dummy-3')
    cy.get('button:contains("Submit")').click()
    cy.get('input[type="file"]').eq(0).should('have.value', '')
    cy.get('input[type="number"]').should('not.exist')
    cy.get('h3:contains("Pages 6 to 7 (from test.pdf pages 1 to 2)")').should('exist')
    cy.get('h4:contains("Page 6")').should('exist')
    cy.get('h4:contains("Page 7")').should('exist')
    cy.get('h4 span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('h4 span.inProgress:contains("in progress")').should('not.exist')
    cy.get('h5 span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('h5 span.inProgress:contains("in progress")').should('not.exist')
    cy.get('div.busy').should('have.length', 2)
    cy.get('div.busy').should('not.exist')

    screenshots('textbook-with-pdf-ranges')

    // Remove exercises
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 2)
    cy.get('h2').eq(0).should('have.text', 'Page 6')
    cy.get('h2').eq(1).should('have.text', 'Page 7')
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Remove")').should('have.length', 7)
    cy.get('button:contains("Remove")').eq(2).click()
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 1)
    cy.get('h2').should('have.text', 'Page 7')
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 7)
    cy.get('button:contains("Remove")').eq(4).click()
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 1)
    cy.get('h2').should('have.text', 'Page 6')
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 7)

    // Remove batch
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Remove")').should('have.length', 7)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Remove")').should('not.exist')
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('p:contains("sorted by page")').should('exist')
    cy.get('h2').should('not.exist')
    cy.get('[data-cy="view-by"]').select('batch')
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 7)

    cy.get('button:contains("View details")').eq(0).click()
    cy.get('h1:contains("Strategy")').should('exist')
    cy.get('a:contains("Dummy Textbook Title")').should('exist').should('have.attr', 'href', '/textbook-1')

    cy.visit('/')
    cy.get('a:contains("Dummy Textbook Title")').should('exist')
    cy.get('a:contains("Batch")').should('not.exist')
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

    screenshots('textbook-with-external-exercises')
  })
})

describe('The edition form for textbooks - with a PDF range', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook-with-pdf-range', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
  })

  it('fixes exercise class', () => {
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-1').click()
    cy.get('a:contains("Dummy Textbook Title")').should('have.attr', 'href', '/textbook-1').click()
    cy.get('span.edit').eq(1).click()
    cy.get('[data-cy="exercise-class"]').should('have.value', 'QCM')
    cy.get('[data-cy="exercise-class"]').select('CochePhrase')
    cy.get('[data-cy="exercise-class"]').should('not.exist')
    cy.get('div.busy').should('exist')
    cy.get('div.busy').should('not.exist')
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-4').click()
    cy.get('a:contains("Dummy Textbook Title")').should('have.attr', 'href', '/textbook-1').click()
  })

  it('removes and re-adds PDF pages', () => {
    cy.get('h5:contains("Exercise")').should('have.length', 4)
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 1).should('have.text', 'Page 40')
    cy.get('[data-cy="view-by"]').select('batch')

    cy.get('h4:contains("Page 40") button:contains("Remove")').should('have.length', 1).click()
    cy.get('h5:contains("Exercise")').should('have.length', 0)
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 0)
    cy.get('[data-cy="view-by"]').select('batch')

    cy.get('h4:contains("Page 40") button:contains("Re-add")').should('have.length', 1).click()
    cy.get('h5:contains("Exercise")').should('have.length', 4)
    cy.get('[data-cy="view-by"]').select('page')
    cy.get('h2').should('have.length', 1).should('have.text', 'Page 40')
    cy.get('[data-cy="view-by"]').select('batch')
  })
})
