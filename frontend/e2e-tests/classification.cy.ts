import { ignoreResizeObserverLoopError, screenshot, visit } from './utils'

describe('The classification batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation,dummy-coche-exercise-classes')
    ignoreResizeObserverLoopError()
    visit('/new-classification-batch')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('looks like this', () => {
    screenshot('classification-batch-creation-page')
  })

  it('opens a .tsv file', () => {
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.tsv')
    cy.get('[data-cy="input-page-number"]').should('have.length', 4)
    cy.get('[data-cy="input-page-number"]').eq(0).should('have.value', '6')
    cy.get('[data-cy="input-exercise-number"]').eq(0).should('have.value', '2')
    cy.get('[data-cy="input-instruction-text"]')
      .eq(0)
      .should('have.value', 'Classe les mots en trois groupes : nom, verbe, adjectif.')
    cy.get('[data-cy="input-statement-text"]')
      .eq(0)
      .should(
        'have.value',
        'verrou ◆ baigner ◆ joli ◆ chaleur ◆ grosse ◆ surveiller ◆ degré ◆ librairie ◆ repas ◆ parler',
      )
    cy.get('[data-cy="input-page-number"]').eq(1).should('have.value', '6')
    cy.get('[data-cy="input-exercise-number"]').eq(1).should('have.value', '4')
    cy.get('[data-cy="input-instruction-text"]')
      .eq(1)
      .should(
        'have.value',
        "Écris une phrase en respectant l'ordre des classes grammaticales indiquées. pronom personnel / verbe / déterminant / nom commun : Je mange une pomme.",
      )
    cy.get('[data-cy="input-statement-text"]')
      .eq(1)
      .should('have.value', 'nom propre / verbe / déterminant / adjectif / nom commun')
    cy.get('[data-cy="input-page-number"]').eq(2).should('have.value', '7')
    cy.get('[data-cy="input-exercise-number"]').eq(2).should('have.value', '11')
    cy.get('[data-cy="input-instruction-text"]')
      .eq(2)
      .should('have.value', 'Ajoute le suffixe –eur aux verbes. Indique la classe des mots fabriqués.')
    cy.get('[data-cy="input-statement-text"]')
      .eq(2)
      .should('have.value', 'nager ➞ ... ◆ tracter ➞ ... ◆ manger ➞ ... ◆ inventer ➞ ... ◆ livrer ➞ ...')
  })

  it('creates a new classification batch without adaptation afterwards and refreshes it until it is done', () => {
    cy.get('[data-cy="run-adaptation"]').select('no')

    cy.get('[data-cy="input-page-number"]').eq(0).type('90', { delay: 0 })
    cy.get('[data-cy="input-exercise-number"]').eq(0).type('1', { delay: 0 })
    cy.get('[data-cy="input-instruction-text"]')
      .eq(0)
      .type('Recopie les deux mots de chaque phrase qui se prononcent de la même façon.', { delay: 0 })
    cy.get('[data-cy="input-statement-text"]')
      .eq(0)
      .type(
        "a. Il a gagné le gros lot à la kermesse des écoles.\nb. À la fin du film, il y a une bonne surprise.\nc. Il a garé sa voiture dans le parking, à droite de la nôtre.\nd. Il m'a invité à venir chez lui.\ne. Mon oncle a un vélo à vendre.",
        { delay: 0 },
      )

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('p:contains("Run adaptation after classification: no")').should('exist')
    cy.get('h2:contains("Input 1 (in progress, will refresh when done)")').should('exist')
    cy.get('h2:contains("Input 1: CocheMot")').should('exist')
    cy.get('p:contains("Adaptation was not requested.")').should('exist')
  })

  it('creates a new classification batch with adaptation afterwards, refreshes it until it is done, then creates settings for the unknown class', () => {
    cy.get('[data-cy="run-adaptation"]').select('yes')
    cy.get('[data-cy="llm-provider"]').select('dummy')
    cy.get('[data-cy="llm-name"]').select('dummy-1')

    cy.get('[data-cy="input-page-number"]').eq(0).type('90', { delay: 0 })
    cy.get('[data-cy="input-exercise-number"]').eq(0).type('1', { delay: 0 })
    cy.get('[data-cy="input-instruction-text"]')
      .eq(0)
      .type('Recopie les deux mots de chaque phrase qui se prononcent de la même façon.', { delay: 0 })
    cy.get('[data-cy="input-statement-text"]')
      .eq(0)
      .type(
        "a. Il a gagné le gros lot à la kermesse des écoles.\nb. À la fin du film, il y a une bonne surprise.\nc. Il a garé sa voiture dans le parking, à droite de la nôtre.\nd. Il m'a invité à venir chez lui.\ne. Mon oncle a un vélo à vendre.",
        { delay: 0 },
      )

    cy.get('[data-cy="input-page-number"]').eq(1).type('90', { delay: 0 })
    cy.get('[data-cy="input-exercise-number"]').eq(1).type('2', { delay: 0 })
    cy.get('[data-cy="input-instruction-text"]')
      .eq(1)
      .type('Recopie uniquement les phrases avec le verbe avoir.', { delay: 0 })
    cy.get('[data-cy="input-statement-text"]')
      .eq(1)
      .type(
        "a. Ce chien a mordu son maître*.\nb. Je rentre à la maison à midi pour déjeuner en famille.\nc. On a froid dans ce sous-bois ombragé.\nd. Il pense toujours qu'il a raison.\ne. Tu joues à chat avec moi ?",
        { delay: 0 },
      )

    cy.get('[data-cy="input-page-number"]').eq(2).type('90', { delay: 0 })
    cy.get('[data-cy="input-exercise-number"]').eq(2).type('3', { delay: 0 })
    cy.get('[data-cy="input-instruction-text"]').eq(2).type('Réponds par vrai ou faux.', { delay: 0 })
    cy.get('[data-cy="input-statement-text"]')
      .eq(2)
      .type('a. Bleu est une couleur\nb. Un triangle a quatre côtés', { delay: 0 })

    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('eq', '/classification-batch-1')
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get(
      'p:contains("Run adaptation after classification: yes, using provider dummy and model dummy-1 with the latest settings for each known exercise class.")',
    ).should('exist')
    cy.get('div.busy').should('exist')
    cy.get('h2:contains("Input 1 (in progress, will refresh when done)")').should('exist')
    cy.get('h2:contains("Input 1: CocheMot")').should('exist')
    cy.get('h2:contains("Input 2: CochePhrase")').should('exist')
    cy.get('h2:contains("Input 3: VraiFaux")').should('exist')
    cy.get('div.busy').should('not.exist')
    cy.get('p:contains("Exercise class VraiFaux does not have adaptation settings yet.")').should('exist')

    cy.visit('/adaptation-2')
    cy.get('a:contains("this batch")').should('have.attr', 'href', '/classification-batch-1')

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="settings-name"]').type('VraiFaux', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('div.busy').should('not.exist')

    cy.visit('/classification-batch-1')
    cy.get(
      'p:contains("Exercise class VraiFaux did not have adaptation settings when this classification batch was submitted.")',
    ).should('exist')
  })
})

describe('The classification batch edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation,dummy-classification-batch')
    ignoreResizeObserverLoopError()
    visit('/classification-batch-1')
  })

  it("allows fixing an exercise's class", () => {
    cy.get('h2:contains("Input 1: CocheMot (classified by model")').should('exist')
    screenshot('classification-batch-edition-page')
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-2')
    cy.get('span.edit').eq(0).click()
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('[data-cy="exercise-class"]').should('have.value', 'CocheMot')
    cy.get('[data-cy="exercise-class"]').select('CochePhrase')
    cy.get('[data-cy="exercise-class"]').should('not.exist')
    cy.get('h2:contains("Input 1: CochePhrase (fixed by Alice")').should('exist')
    cy.get('div.busy').should('exist')
    cy.get('div.busy').should('not.exist')
    cy.get('a:contains("View details")').eq(0).should('have.attr', 'href', '/adaptation-3')

    cy.get('h2:contains("Input 2: NoSettings (classified by model")').should('exist')
    cy.get(':contains("Exercise class NoSettings does not have adaptation settings yet.")').should('exist')
    cy.get('span.edit').eq(1).click()
    cy.get('[data-cy="exercise-class"]').should('have.value', 'NoSettings')
    cy.get('[data-cy="exercise-class"]').select('CocheMot')
    cy.get('[data-cy="exercise-class"]').should('not.exist')
    cy.get('h2:contains("Input 2: CocheMot (fixed by Alice")').should('exist')
    cy.get('div.busy').should('exist')
    cy.get('div.busy').should('not.exist')
    cy.get(':contains("Exercise class NoSettings does not have adaptation settings yet.")').should('not.exist')
    cy.get('a:contains("View details")').eq(1).should('have.attr', 'href', '/adaptation-4')
    cy.get('span.edit').eq(1).click()
    cy.get('[data-cy="exercise-class"]').should('have.value', 'CocheMot')
    cy.get('[data-cy="exercise-class"]').select('NoSettings')
    cy.get('[data-cy="exercise-class"]').should('not.exist')
    cy.get('h2:contains("Input 2: NoSettings (fixed by Alice")').should('exist')
    cy.get(':contains("Exercise class NoSettings does not have adaptation settings yet.")').should('exist')
  })
})
