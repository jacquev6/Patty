describe('The adaptation creation page', () => {
  beforeEach(() => {
    cy.viewport(800, 500)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation-strategy,default-adaptation-input')

    Cypress.on('uncaught:exception', error => {
      if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
        // @todo Deep dive into this issue: avoid the error instead of ignoring it.
        // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
        return false
      } else {
        return true
      }
    })

    cy.visit('/new-adaptation')
  })

  it('looks like this', () => {
    cy.compareSnapshot(`adaptation-creation-page.${Cypress.browser.name}`)
  })

  it('remembers the last strategy used', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')

    cy.get('@system-prompt').type(' Blih blih.', {delay: 0})
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
    cy.get('button:contains("Submit")').click()
    cy.get('h1:contains("Adapted exercise")').should('exist')

    cy.visit('/new-adaptation')
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
  })

  it('remembers the last input used', () => {
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('@input-text').type('Blih blih.', {delay: 0})
    cy.get('@input-text').should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\nBlih blih.')
    cy.get('button:contains("Submit")').click()
    cy.get('h1:contains("Adapted exercise")').should('exist')

    cy.visit('/new-adaptation')
    cy.get('@input-text').should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\nBlih blih.')
  })
})


describe('The adaptation edition page', () => {
  beforeEach(() => {
    cy.viewport(1280, 1024)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')

    Cypress.on('uncaught:exception', error => {
      if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
        // @todo Deep dive into this issue: avoid the error instead of ignoring it.
        // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
        return false
      } else {
        return true
      }
    })
  })

  it('looks like this', () => {
    cy.visit('/adaptation-1')

    cy.compareSnapshot(`adaptation-edition-page.${Cypress.browser.name}`)
  })

  it('displays "Not found" when the adaptation does not exist', () => {
    cy.visit('/adaptation-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('enables the "submit adjustment" button', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').as('user-prompt')
    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')

    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
    cy.get('@user-prompt').type('Blah.', {delay: 0})
    cy.get('@user-prompt').should('have.value', 'Blah.')
    cy.get('@submit-adjustment').should('be.enabled')
    cy.get('@user-prompt').type('{selectAll}{del}', {delay: 0})
    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
  })

  it('submits and rewinds adjustments', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').as('user-prompt')
    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')

    cy.get('@user-prompt').type('Blah.', {delay: 0})
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist')
    cy.get('@user-prompt').type('Bleh.', {delay: 0})
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('not.exist')
    cy.get('div.user-prompt:contains("Bleh.")').should('exist')
    cy.get('div.user-prompt:contains("Bleh.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Bleh.")').should('not.exist')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Blah.")').should('not.exist')
  })

  const unformattedJson = '{"format":"v1","instructions":{"lines":[{"contents":[{"kind":"text","text":"Blah"}]}]},"wording":{"pages":[]},"references":null}'
  const formattedJson = '{\n  "format": "v1",\n  "instructions": {"lines": [{"contents": [{"kind": "text", "text": "Blah"}]}]},\n  "wording": {"pages": []},\n  "references": null\n}'

  it('reformats manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@manual-edition').type('{selectAll}').type(unformattedJson, {delay: 0, parseSpecialCharSequences: false})
    cy.get('@manual-edition').should('have.value', unformattedJson)
    cy.get('button[data-cy="reformat-manual-edition"]').click()
    cy.get('@manual-edition').should('have.value', formattedJson)
  })

  it('saves manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@manual-edition').type('{selectAll}').type(unformattedJson, {delay: 0, parseSpecialCharSequences: false})

    cy.visit('/adaptation-1')

    cy.get('@manual-edition').should('have.value', formattedJson)
  })

  it('forbids adjustments on manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')
    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@submit-adjustment').should('exist')
    cy.get('@manual-edition').type('Blih blih.', {delay: 0})
    cy.get('@submit-adjustment').should('not.exist')
    cy.get('[data-cy="reset-manual-edition"]').click()
    cy.get('@submit-adjustment').should('exist')
  })
})
