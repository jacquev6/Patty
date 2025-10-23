import { ignoreResizeObserverLoopError, visit, visitExport, screenshot, loadFixtures } from './utils'

describe('The autonomous HTML for a single adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-adaptation'])
    ignoreResizeObserverLoopError()
  })

  it('is downloadable', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/P42Ex5.html`).should('not.exist')

    visit('/adaptation-1')
    cy.get('a:contains("standalone HTML")').click()
    cy.wait(1000)
    cy.get('a:contains("standalone HTML")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/P42Ex5.html`)
  })

  it('remembers student answers', () => {
    visitExport('/api/export/adaptation/1.html')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    visitExport('/api/export/adaptation/1.html')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.get('.control').eq(1).click()
    cy.get('button:contains("Effacer mes réponses")').click()
    cy.get(':contains("Les feuilles sont chahutées par")').should('exist')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
  })

  it('forgets student answers when the exercise is modified', () => {
    visitExport('/api/export/adaptation/1.html')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    visit('/adaptation-1')
    cy.get('[data-cy="manual-edition"]')
      .type('{selectall}{backspace}', { delay: 0, force: true })
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

    visitExport('/api/export/adaptation/1.html')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', '....')
  })

  it('has a vertical scrollbar when required', () => {
    cy.viewport(1600, 1000)
    visitExport('/api/export/adaptation/1.html')
    screenshot('adapted-exercise-without-scrollbar')
    cy.viewport(1600, 400)
    screenshot('adapted-exercise-with-scrollbar')
  })
})

describe('The exported data for an adaptation batch', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
  })

  it('can be downloaded as autonomous HTML', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-adaptation-batch-1.html`).should('not.exist')

    visit('/adaptation-batch-1')
    cy.get('a:contains("standalone HTML")').click()
    cy.wait(1000)
    cy.get('a:contains("standalone HTML")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-adaptation-batch-1.html`)
  })

  it('can be downloaded as JSON', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-adaptation-batch-1-adapted-exercises.json`).should(
      'not.exist',
    )

    visit('/adaptation-batch-1')
    cy.get('a:contains("JSON data for adapted exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("JSON data for adapted exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-adaptation-batch-1-adapted-exercises.json`)
  })

  it('remembers student answers ands shares them with the autonomous HTML for a single adaptation', () => {
    visitExport('/api/export/sandbox-adaptation-batch-1.html')
    cy.get('a:contains("Exercice P42Ex5")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    visitExport('/api/export/sandbox-adaptation-batch-1.html')
    cy.get('a:contains("Exercice P42Ex5")').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    visitExport('/api/export/adaptation/1.html')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')
  })
})

describe('The exported data for a classification batch', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-classification-batch'])
    ignoreResizeObserverLoopError()
  })

  it('the adapted exercises can be downloaded as autonomous HTML', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1.html`).should('not.exist')

    visit('/classification-batch-1')
    cy.get('a:contains("standalone HTML")').click()
    cy.wait(1000)
    cy.get('a:contains("standalone HTML")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1.html`)
  })

  it('the classified exercises can be downloaded as TSV', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1-classified-exercises.tsv`).should(
      'not.exist',
    )

    visit('/classification-batch-1')
    cy.get('a:contains("TSV data for classified exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("TSV data for classified exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1-classified-exercises.tsv`)
  })

  it('the adapted exercises can be downloaded as JSON', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1-adapted-exercises.json`).should(
      'not.exist',
    )

    visit('/classification-batch-1')
    cy.get('a:contains("JSON data for adapted exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("JSON data for adapted exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-classification-batch-1-adapted-exercises.json`)
  })
})

describe('The exported data for an extraction batch', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['empty-extraction-batch'])
    ignoreResizeObserverLoopError()
  })

  it('the adapted exercises can be downloaded as autonomous HTML', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1.html`).should('not.exist')

    visit('/extraction-batch-1')
    cy.get('a:contains("standalone HTML")').click()
    cy.wait(1000)
    cy.get('a:contains("standalone HTML")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1.html`)
  })

  it('the extracted exercises can be downloaded as JSON', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-extracted-exercises.json`).should(
      'not.exist',
    )

    visit('/extraction-batch-1')
    cy.get('a:contains("JSON data for extracted exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("JSON data for extracted exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-extracted-exercises.json`)
  })

  it('the extracted exercises can be downloaded as TSV', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-extracted-exercises.tsv`).should(
      'not.exist',
    )

    visit('/extraction-batch-1')
    cy.get('a:contains("TSV data for extracted exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("TSV data for extracted exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-extracted-exercises.tsv`)
  })

  it('the classified exercises can be downloaded as TSV', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-classified-exercises.tsv`).should(
      'not.exist',
    )

    visit('/extraction-batch-1')
    cy.get('a:contains("TSV data for classified exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("TSV data for classified exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-classified-exercises.tsv`)
  })

  it('the adapted exercises can be downloaded as JSON', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-adapted-exercises.json`).should(
      'not.exist',
    )

    visit('/extraction-batch-1')
    cy.get('a:contains("JSON data for adapted exercises")').click()
    cy.wait(1000)
    cy.get('a:contains("JSON data for adapted exercises")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/sandbox-extraction-batch-1-adapted-exercises.json`)
  })
})

describe('The autonomous HTML for a textbook', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-textbook-with-text-exercise-numbers'])
  })

  it('is downloadable', () => {
    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/Dummy Textbook Title.html`).should('not.exist')

    visit('/textbook-1')
    cy.get('button:contains("Download")').click()
    cy.wait(1000)
    cy.get('button:contains("Download")').should('exist')
    cy.readFile(`${Cypress.config('downloadsFolder')}/Dummy Textbook Title.html`)
  })

  it('displays the textbook title', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('p:contains("Title")').should('have.text', 'Dummy Textbook Title')
  })

  it('displays nothing', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('p.message').should('not.exist')
    cy.get('a').should('have.length', 0)
  })

  it('displays "La page 27 n\'existe pas."', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('27')
    cy.get('p.message').should('exist').should('have.text', "La page 27 n'existe pas.")
  })

  it('filters exercises by page', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('42')
    cy.get('a').should('have.length', 4)
    cy.get('a').eq(0).should('have.text', 'Auto-dictée')
    cy.get('a').eq(1).should('have.text', 'Exo identifié par texte / 5')
    cy.get('a').eq(2).should('have.text', 'Exercice 5')
    cy.get('a').eq(3).should('have.text', 'Exercice 6')

    cy.get('[data-cy="page-number-filter"]').type('{selectAll}40')
    cy.get('a').should('have.length', 3)
    cy.get('a').eq(0).should('have.text', 'Exercice 4')
    cy.get('a').eq(1).should('have.text', 'Exercice 6')
    cy.get('a').eq(2).should('have.text', 'Exercice 8')
  })

  it('has working links', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('42')
    cy.get('a').eq(3).should('have.attr', 'target', '_blank').invoke('removeAttr', 'target').click()
    cy.location('hash').should('eq', '#/P42Ex6?closable=true')
    cy.get(':contains("Complète avec")').should('exist')
  })

  it('has working links - even when the exercice number has URL-incompatible characters', () => {
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('42')
    cy.get('a').eq(1).should('have.attr', 'target', '_blank').invoke('removeAttr', 'target').click()
    cy.location('hash').should('eq', '#/P42ExExo%20identifi%C3%A9%20par%20texte%20%2F%205?closable=true')
    cy.get(':contains("Complète avec")').should('exist')
  })

  it('has working links to external exercises', () => {
    visit('/textbook-1')
    cy.get("input[data-cy='external-files']").selectFile([
      'e2e-tests/inputs/P40Ex1.docx',
      'e2e-tests/inputs/P40Ex7.docx',
    ])
    cy.get('.busy').should('not.exist')

    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('40')
    cy.get('a').should('have.length', 5)
    cy.get('a').eq(0).should('have.text', 'Exercice 1 - Word')
    cy.get('a').eq(1).should('have.text', 'Exercice 4')
    cy.get('a').eq(2).should('have.text', 'Exercice 6')
    cy.get('a').eq(3).should('have.text', 'Exercice 7 - Word')
    cy.get('a').eq(4).should('have.text', 'Exercice 8')

    cy.task('deleteFolder', Cypress.config('downloadsFolder'))
    cy.readFile(`${Cypress.config('downloadsFolder')}/P40Ex1.docx`).should('not.exist')
    cy.get('a').eq(0).click()
    cy.readFile('e2e-tests/inputs/P40Ex1.docx').then((expected) => {
      cy.readFile(`${Cypress.config('downloadsFolder')}/P40Ex1.docx`).should('deep.equal', expected)
    })
  })
})
