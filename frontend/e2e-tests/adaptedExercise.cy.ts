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

  it('forgets student answers when the exercise is modified', () => {
    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/adaptation-1')
    cy.get('[data-cy="manual-edition"]')
      .type('{selectall}{backspace}', { delay: 0 })
      .type(
        `{
          "format": "v1",
          "instruction": {
            "lines": [
              {
                "contents": [
                  {"kind": "text", "text": "Complète"},
                  {"kind": "whitespace"},
                  {"kind": "text", "text": "avec"},
                  {"kind": "whitespace"},
                  {
                    "kind": "choice",
                    "contents": [
                      {"kind": "text", "text": "le"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "vent"}
                    ]
                  },
                  {"kind": "whitespace"},
                  {"kind": "text", "text": "ou"},
                  {"kind": "whitespace"},
                  {
                    "kind": "choice",
                    "contents": [
                      {"kind": "text", "text": "la"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "pluie"}
                    ]
                  }
                ]
              }
            ]
          },
          "example": null,
          "hint": null,
          "statement": {
            "pages": [
              {
                "lines": [
                  {
                    "contents": [
                      {"kind": "text", "text": "a"},
                      {"kind": "text", "text": "."},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "Les"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "feuilles"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "sont"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "chahutées"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "par"},
                      {"kind": "whitespace"},
                      {
                        "kind": "multipleChoicesInput",
                        "choices": [
                          {
                            "contents": [
                              {"kind": "text", "text": "le"},
                              {"kind": "whitespace"},
                              {"kind": "text", "text": "VENT"}
                            ]
                          },
                          {
                            "contents": [
                              {"kind": "text", "text": "la"},
                              {"kind": "whitespace"},
                              {"kind": "text", "text": "pluie"}
                            ]
                          }
                        ],
                        "showChoicesByDefault": false
                      }
                    ]
                  },
                  {
                    "contents": [
                      {"kind": "text", "text": "b"},
                      {"kind": "text", "text": "."},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "Les"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "vitres"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "sont"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "mouillées"},
                      {"kind": "whitespace"},
                      {"kind": "text", "text": "par"},
                      {"kind": "whitespace"},
                      {
                        "kind": "multipleChoicesInput",
                        "choices": [
                          {
                            "contents": [
                              {"kind": "text", "text": "le"},
                              {"kind": "whitespace"},
                              {"kind": "text", "text": "vent"}
                            ]
                          },
                          {
                            "contents": [
                              {"kind": "text", "text": "la"},
                              {"kind": "whitespace"},
                              {"kind": "text", "text": "pluie"}
                            ]
                          }
                        ],
                        "showChoicesByDefault": false
                      }
                    ]
                  }
                ]
              }
            ]
          },
          "reference": null
        }`,
        { delay: 0, parseSpecialCharSequences: false },
      )
    cy.wait(500)

    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', '....')
  })
})

describe('The autonomous HTML for a batch', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
  })

  it('remembers student answers ands shares them with the autonomous HTML for a single adaptation', () => {
    cy.visit('/api/adaptation/export/batch-1.html?download=false')
    cy.get('a:contains("Exercise P42Ex5")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/batch-1.html?download=false')
    cy.get('a:contains("Exercise P42Ex5")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/api/adaptation/export/adaptation-1.html?download=false')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')
  })
})

describe('The autonomous HTML for a textbook', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-textbook')
    cy.visit('/api/adaptation/export/textbook-1.html?download=false')
  })

  it('displays the textbook title', () => {
    cy.get('p:contains("Livre")').should('have.text', 'Livre: Dummy Textbook Title')
  })

  it('displays nothing', () => {
    cy.get('p.message').should('not.exist')
    cy.get('a').should('have.length', 0)
  })

  it('displays "Indique le numéro de la page."', () => {
    cy.get('[data-cy="exercise-number-filter"]').type('42', { delay: 0 })
    cy.get('p.message').should('exist').should('have.text', 'Indique le numéro de la page.')
  })

  it('displays "La page 27 n\'existe pas."', () => {
    cy.get('[data-cy="page-number-filter"]').type('27', { delay: 0 })
    cy.get('p.message').should('exist').should('have.text', "La page 27 n'existe pas.")
  })

  it('displays "L\'exercice numéro 12 n\'existe pas."', () => {
    cy.get('[data-cy="page-number-filter"]').type('40', { delay: 0 })
    cy.get('[data-cy="exercise-number-filter"]').type('12', { delay: 0 })
    cy.get('p.message').should('exist').should('have.text', "L'exercice numéro 12 n'existe pas.")
  })

  it('filters exercises by page', () => {
    cy.get('[data-cy="page-number-filter"]').type('42', { delay: 0 })
    cy.get('a').should('have.length', 2)
    cy.get('a').eq(0).should('have.text', 'Exercice 5')
    cy.get('a').eq(1).should('have.text', 'Exercice 6')

    cy.get('[data-cy="page-number-filter"]').type('{selectAll}40', { delay: 0 })
    cy.get('a').should('have.length', 4)
    cy.get('a').eq(0).should('have.text', 'Exercice 4')
    cy.get('a').eq(1).should('have.text', 'Exercice 6')
    cy.get('a').eq(2).should('have.text', 'Exercice 8')
    cy.get('a').eq(3).should('have.text', 'Exercice 30')
  })

  it('filters exercises by page and number', () => {
    cy.get('[data-cy="page-number-filter"]').type('42', { delay: 0 })
    cy.get('[data-cy="exercise-number-filter"]').type('6', { delay: 0 })
    cy.get('a').should('have.length', 1)
    cy.get('a').eq(0).should('have.text', 'Exercice 6')
  })

  it('has working links', () => {
    cy.get('[data-cy="page-number-filter"]').type('42', { delay: 0 })
    cy.get('[data-cy="exercise-number-filter"]').type('6', { delay: 0 })
    cy.get('a').should('have.attr', 'target', '_blank').invoke('removeAttr', 'target').click()
    cy.location('hash').should('eq', '#/P42Ex6')
    cy.get(':contains("Complète avec")').should('exist')
  })
})
