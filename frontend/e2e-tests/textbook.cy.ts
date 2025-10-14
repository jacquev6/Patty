import { ignoreResizeObserverLoopError, loadFixtures, screenshot, visit } from './utils'

describe('The creation form for textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-branch', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/new-textbook')
  })

  it('creates a multi-PDFs textbook with only a title', () => {
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="textbook-title"]').type('Mutli-PDFs', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('label:contains("Single PDF") input').should('not.be.checked')
    cy.get('label:contains("Multiple PDFs") input').should('not.be.checked').check()
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1 span').should('have.text', 'Mutli-PDFs')
    cy.get('h2:contains("New textbook PDF")').should('exist')
    cy.get('h2:contains("Existing textbook PDFs")').should('exist')

    cy.visit('/')
    cy.get('li:contains("Mutli-PDFs")').should('exist').should('contain', 'Mutli-PDFs (created by Alice on')
  })

  it('creates a multi-PDFs textbook with all fields', () => {
    cy.get('[data-cy="textbook-title"]').type('The title', { delay: 0 })
    cy.get('[data-cy="textbook-publisher"]').type('Dummy publisher', { delay: 0 })
    cy.get('[data-cy="textbook-year"]').type('2023', { delay: 0 })
    cy.get('[data-cy="textbook-isbn"]').type('978-3-16-148410-0', { delay: 0 })
    cy.get('[data-cy="textbook-pages-count"]').type('76', { delay: 0 })
    cy.get('label:contains("Multiple PDFs") input').check()
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1 span').should('have.text', 'The title (76 pages), Dummy publisher, 2023 (ISBN: 978-3-16-148410-0)')
    cy.get('h2:contains("New textbook PDF")').should('exist')

    cy.visit('/')
    cy.get('li:contains("The title")')
      .should('exist')
      .should('contain', 'The title (76 pages), Dummy publisher, 2023 (created by Alice on')
  })

  it('creates a single-PDF textbook with only a title', () => {
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('[data-cy="textbook-title"]').type('Single-PDF', { delay: 0 })
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('label:contains("Multiple PDFs") input').should('not.be.checked')
    cy.get('label:contains("Single PDF") input').should('not.be.checked').check()
    cy.get('button:contains("Submit")').should('be.disabled')
    cy.get('input[type="file"]').eq(0).selectFile('e2e-tests/inputs/test.pdf')
    cy.get('button:contains("Submit")').should('be.enabled').click()
    cy.location('pathname').should('equal', '/textbook-1')
    cy.get('h1 span').should('have.text', 'Single-PDF')
    cy.get('h2:contains("New textbook PDF")').should('not.exist')
    cy.get('h2:contains("Existing textbook PDFs")').should('not.exist')
    cy.get('li a:contains("2")').should('exist')
    screenshot('single-pdf-textbook')

    cy.visit('/')
    cy.get('li:contains("Single-PDF")').should('exist').should('contain', 'Single-PDF (created by Alice on')
  })
})

describe('The edition form for multi-PDFs textbooks - empty', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
  })

  it('adds and removes PDF ranges', () => {
    screenshot('multi-pdfs-textbook--empty')

    cy.get('input[type="file"]').eq(0).selectFile('e2e-tests/inputs/test.pdf')
    cy.get('p:contains("i.e. 2 in textbook")').should('exist')
    cy.get('input[type="number"]').eq(1).type('{selectAll}6').blur()
    cy.get('p:contains("i.e. 7 in textbook")').should('exist')
    cy.get('[data-cy="extraction"] [data-cy="llm-provider"]').select('dummy')
    cy.get('[data-cy="extraction"] [data-cy="llm-name"]').select('dummy-1')
    cy.get('[data-cy="adaptation"] [data-cy="llm-provider"]').select('dummy')
    cy.get('[data-cy="adaptation"] [data-cy="llm-name"]').select('dummy-3')
    cy.get('button:contains("Submit")').click()
    cy.get('input[type="file"]').eq(0).should('have.value', '')
    cy.get('input[type="number"]').should('not.exist')
    cy.get('h3:contains("Pages 6 to 7 (from test.pdf pages 1 to 2)")').should('exist')
    cy.get('li:contains("6")').should('exist')
    cy.get('li:contains("7")').should('exist')
    cy.get('li span.inProgress:contains("in progress")').should('have.length', 2)
    cy.get('li span.inProgress:contains("in progress")', { timeout: 10000 }).should('not.exist')
    cy.get(':contains("in progress")').should('not.exist')
    cy.get('div.busy').should('not.exist')

    // Remove exercises
    cy.get('li a:contains("6")').click()
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('a:contains("Dummy Textbook Title")').click()
    cy.get('button:contains("Remove")').should('have.length', 3)

    screenshot('multi-pdfs-textbook--with-pdf-ranges')

    // Remove batch
    cy.visit('/textbook-1/page-6')
    cy.get('h2').should('have.length', 2)
    cy.get('a:contains("Dummy Textbook Title")').click()
    cy.get('button:contains("Remove")').should('have.length', 3)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Remove")').should('not.exist')
    cy.visit('/textbook-1/page-6')
    cy.get('h2').should('have.length', 0)
    cy.get('a:contains("Dummy Textbook Title")').click()
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Remove")').should('have.length', 3)
    cy.visit('/textbook-1/page-6')
    cy.get('h2').should('have.length', 2)
    cy.get('a:contains("Dummy Textbook Title")').click()

    cy.get('li a:contains("6")').click()
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('h1:contains("Adapted exercise")').should('exist')
    cy.get('a:contains("Dummy Textbook Title")').should('exist').should('have.attr', 'href', '/textbook-1')
    cy.get('a:contains("Page 6")').should('exist').should('have.attr', 'href', '/textbook-1/page-6')

    cy.visit('/')
    cy.get('a:contains("Dummy Textbook Title")').should('exist')
    cy.get('a:contains("Batch")').should('not.exist')
  })

  it('adds and removes external exercises', () => {
    cy.get('p:contains("Files must be named like")').should('exist')
    cy.get("input[data-cy='external-files']").selectFile([
      'e2e-tests/inputs/P40Ex1.docx',
      'e2e-tests/inputs/bad-name.docx',
      'e2e-tests/inputs/P40Ex7.docx',
    ])
    cy.get('.busy').should('not.exist')
    cy.get('p:contains("Files must be named like")').should('have.class', 'error')

    cy.get("input[data-cy='external-files']").selectFile([
      'e2e-tests/inputs/P40Ex1.docx',
      'e2e-tests/inputs/P40Ex7.docx',
    ])
    cy.get('p:contains("Files must be named like")').should('not.have.class', 'error')
    cy.get('.busy').should('not.exist')

    cy.visit('/textbook-1/page-40')
    cy.get('h1').should('contain', 'page 40')
    cy.get('h2').should('have.length', 2)
    cy.get('h2').eq(0).should('contain', 'Exercise 1').should('not.contain', 'removed')
    cy.get('h2').eq(1).should('contain', 'Exercise 7').should('not.contain', 'removed')
    cy.get('label:contains("Show only exercises not yet approved") input').should('be.disabled')
    screenshot('multi-pdfs-textbook--page-with-external-exercises')

    cy.get('a:contains("Dummy Textbook Title")').click()
    cy.get('button:contains("Remove")').should('have.length', 2)
    cy.get('button:contains("Remove")').eq(0).click()

    cy.visit('/textbook-1/page-40')
    cy.get('h1').should('contain', 'page 40')
    cy.get('h2').should('have.length', 2)
    cy.get('h2').eq(0).should('contain', 'Exercise 1').should('contain', 'removed')
    cy.get('h2').eq(1).should('contain', 'Exercise 7').should('not.contain', 'removed')

    cy.get('button:contains("Remove")').should('have.length', 1)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Re-add")').should('have.length', 2)
    cy.get('button:contains("Re-add")').eq(0).click()

    cy.get('h1').should('contain', 'page 40')
    cy.get('h2').should('have.length', 2)
    cy.get('h2').eq(0).should('contain', 'Exercise 1').should('not.contain', 'removed')
    cy.get('h2').eq(1).should('contain', 'Exercise 7').should('contain', 'removed')

    cy.get('a:contains("Dummy Textbook Title")').click()
    screenshot('multi-pdfs-textbook--with-external-exercises')
  })
})

describe('The edition form for multi-PDFs textbooks - with a PDF range', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook-with-pdf-range', 'dummy-extraction-strategy', 'dummy-coche-exercise-classes'])
    ignoreResizeObserverLoopError()
    visit('/textbook-1')
    cy.get('li a:contains("40")').should('have.attr', 'href', '/textbook-1/page-40').click()
  })

  it('has adaptation pages that look like this', () => {
    cy.get('a:contains("View details")').eq(0).click()
    screenshot(`adaptation`)
  })

  it('fixes exercise class', () => {
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-1').click()
    cy.get('a:contains("Dummy Textbook Title")').should('have.attr', 'href', '/textbook-1')
    cy.get('a:contains("Page 40")').should('have.attr', 'href', '/textbook-1/page-40').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("Unapprove")').should('have.length', 1)
    cy.get('span.edit').eq(1).click()
    cy.get('[data-cy="exercise-class"]').should('have.value', 'QCM')
    cy.get('[data-cy="exercise-class"]').select('CochePhrase')
    cy.get('[data-cy="exercise-class"]').should('not.exist')
    cy.get('div.busy', { timeout: 10000 }).should('exist') // This fails sometimes. @todo Fix it. There might be a race condition.
    cy.get('div.busy').should('not.exist')
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Unapprove")').should('not.exist')
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-4').click()
    cy.get('a:contains("Dummy Textbook Title")').should('have.attr', 'href', '/textbook-1')
    cy.get('a:contains("Page 40")').should('have.attr', 'href', '/textbook-1/page-40')
  })

  it('removes and re-adds PDF pages', () => {
    cy.get('h2').should('have.length', 4)
    cy.get('a:contains("Dummy Textbook Title")').click()

    cy.get('li a:contains("40")').should('exist')
    cy.get('li:contains("40") button:contains("Remove")').should('have.length', 1).click()
    cy.get('li a:contains("40")').should('not.exist')

    cy.get('li:contains("40") button:contains("Re-add")').should('have.length', 1).click()
    cy.get('li a:contains("40")').click()
    cy.get('h2').should('have.length', 4)
    cy.get('a:contains("Dummy Textbook Title")').click()
  })

  it('approves and unapproves exercises', () => {
    // Make sure all exercises are adapted
    cy.get('span.edit').eq(4).click()
    cy.get('select').eq(1).select('CocheMot')
    cy.get('button:contains("Approve")', { timeout: 10000 }).should('have.length', 4)
    cy.get('div.main').scrollTo('top')

    cy.get('label:contains("Show all exercises") input').check()
    cy.get('h2:contains("Exercise")').should('have.length', 4)
    cy.get('label:contains("Show only exercises not yet approved") input').check()
    cy.get('h2:contains("Exercise")').should('have.length', 4)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('h2:contains("Exercise")').should('have.length', 3)
    cy.get('label:contains("Show all exercises") input').check()
    cy.get('h2:contains("Exercise")').should('have.length', 4)
    cy.get('button:contains("Unapprove")').eq(0).click()
    cy.get('label:contains("Show only exercises not yet approved") input').check()
    cy.get('h2:contains("Exercise")').should('have.length', 4)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('h2:contains("Exercise")').should('have.length', 3)
    cy.get('label:contains("Show all exercises") input').check()
    cy.get('div.main').scrollTo('top')
    screenshot('approved-exercise')
    cy.get('label:contains("Show only exercises not yet approved") input').check()
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 1)
    cy.get('label:contains("Show only exercises not yet approved") input').should('be.enabled').should('be.checked')
    cy.get('label:contains("Show all exercises") input').should('not.be.checked')
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 0)
    cy.get('label:contains("Show only exercises not yet approved") input').should('be.disabled')
    cy.get('label:contains("Show all exercises") input').should('be.checked')
    cy.get('h2:contains("Exercise")').should('have.length', 4)
    cy.get('button:contains("Approve")').should('have.length', 0)
  })

  it('unapproves an exercise when an adjustment is made or deleted', () => {
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('[data-cy="user-prompt"]').click().type('Adjust!', { delay: 0 })
    cy.get('[data-cy="submit-adjustment"]').click()
    cy.get('p:contains("Adjust!")').should('exist')
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('div:contains("❌")').last().click()
    cy.get('p:contains("Adjust!")').should('not.exist')
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
  })

  it('unapproves an exercise when its JSON is set manually or reset', () => {
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('[data-cy="manual-edition"]').type('{selectAll}Not JSON', { delay: 0, force: true })
    cy.get(':contains("Syntax error")').should('exist')
    cy.wait(500)
    // Not saved => not invalidated
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('[data-cy="manual-edition"]')
      .type('{selectAll}', { delay: 0, force: true })
      .type('{}', { delay: 0, force: true, parseSpecialCharSequences: false })
    cy.get(':contains("Validation errors")').should('exist')
    cy.wait(500)
    // Not saved => not invalidated
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('button:contains("Reset")').should('be.disabled')
    cy.get('[data-cy="manual-edition"]')
      .type('{selectAll}', { delay: 0, force: true })
      .type(
        '{"format":"v1","instruction":{"lines":[]},"example":null,"hint":null,"statement":{"pages":[]},"reference":null}',
        { delay: 0, force: true, parseSpecialCharSequences: false },
      )
    cy.get('button:contains("Reset")').should('be.enabled')
    cy.wait(500)
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("View details")').eq(0).click()
    cy.get('button:contains("Reset")').click()
    cy.get('button:contains("Reset")').should('be.disabled')
    cy.wait(500)
    cy.get('a:contains("Page 40")').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
  })

  it('unapproves an exercise when it is removed and re-added', () => {
    cy.get('button:contains("Approve")').should('have.length', 3)
    cy.get('button:contains("Approve")').eq(0).click()
    cy.get('button:contains("Approve")').should('have.length', 2)
    cy.get('button:contains("Remove")').eq(0).click()
    cy.get('button:contains("Re-add")').should('have.length', 1)
    cy.get('button:contains("Re-add")').click()
    cy.get('button:contains("Approve")').should('have.length', 3)
  })
})
