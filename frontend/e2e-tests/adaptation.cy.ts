describe('The adaptation creation form', () => {
  beforeEach(() => {
    cy.viewport(1280, 1024)

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
  })

  it('remembers the last strategy used', () => {
    cy.visit('/new-adaptation')

    cy.get('textarea[data-cy="system-prompt"]').as('system-prompt')
    cy.get('@system-prompt').type(' Blih blih.', {delay: 0})
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')

    cy.get('button:contains("Submit")').click()
    cy.get('h1:contains("Adapted exercise")').should('exist')

    cy.visit('/new-adaptation')
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
  })

  it('remembers the last input used', () => {
    cy.visit('/new-adaptation')

    cy.get('textarea[data-cy="input-text"]').as('input-text')
    cy.get('@input-text').type('Blih blih.', {delay: 0})
    cy.get('@input-text').should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\nBlih blih.')

    cy.get('button:contains("Submit")').click()
    cy.get('h1:contains("Adapted exercise")').should('exist')

    cy.visit('/new-adaptation')
    cy.get('@input-text').should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\nBlih blih.')
  })
})
