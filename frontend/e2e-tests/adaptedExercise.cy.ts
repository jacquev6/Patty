describe('The autonomous HTML', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')
  })

  it('remembers student answers', () => {
    cy.visit('/api/adaptation/export/1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')
  })
})
