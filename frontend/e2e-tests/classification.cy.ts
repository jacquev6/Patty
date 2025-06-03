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
    // @todo Submit the adaptation using the new settings.
  })
})
