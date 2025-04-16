describe('The autonomous HTML for a single adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')
  })

  it('remembers student answers', () => {
    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')
  })
})

describe('The autonomous HTML for a batch', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
  })

  it('remembers student answers ands shares them with the autonomous HTML for a single adaptation', () => {
    cy.visit('/api/adaptation/export/batch-1.html?download=false')
    cy.get('a:contains("Exercise 1")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/batch-1.html?download=false')
    cy.get('a:contains("Exercise 1")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')
  })
})
