// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import type { AdaptedExercise } from '@/frontend/ApiClient'
import { loadFixtures, visit, visitExport, ignoreResizeObserverLoopError, screenshot } from './utils'

const dataUriRegex = /^data:image\/png;base64,/

function checkImagesFrontend(length: number) {
  cy.get('img').should('have.length', length)
  cy.get('img')
    .eq(length - 4)
    .should('have.attr', 'src')
    .and('match', /^\/api\/files\/3\.png\?token=.*$/)
  cy.get('img')
    .eq(length - 3)
    .should('have.attr', 'src')
    .and('match', /^\/api\/files\/2\.png\?token=.*$/)
  cy.get('img')
    .eq(length - 2)
    .should('have.attr', 'src')
    .and('match', /^\/api\/files\/1\.png\?token=.*$/)
  cy.get('img')
    .eq(length - 1)
    .should('have.attr', 'src', '/src/adapted-exercise/arrow.png')
}

function checkImagesExport() {
  cy.get('img').should('have.length', 4)
  cy.get('img').eq(0).should('have.attr', 'src').and('match', dataUriRegex)
  cy.get('img').eq(1).should('have.attr', 'src').and('match', dataUriRegex)
  cy.get('img').eq(2).should('have.attr', 'src').and('match', dataUriRegex)
  cy.get('img').eq(3).should('have.attr', 'src').and('match', dataUriRegex)
}

describe('Patty', () => {
  beforeEach(() => {
    ignoreResizeObserverLoopError()
    loadFixtures(['extraction-seed-data-v2', 'adaptation-seed-data', 'dummy-rcimage-exercise-class'])
  })

  it('extracts images in sandbox', () => {
    visit('/new-extraction-batch')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/images.pdf')
    cy.get('[data-cy="llm-name"]').eq(0).select('dummy-for-images')
    cy.get('[data-cy="run-adaptation"]').select('yes')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-for-images')
    cy.get('button:contains("Submit")').click()
    cy.contains('in progress').should('exist')
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    cy.get('a:contains("View details")').should('have.attr', 'href', '/adaptation-2')
    checkImagesFrontend(15)
    cy.wait(500) // Give time to display images
    screenshot('images-sandbox-batch-frontend-1')
    cy.get('.column').eq(1).scrollTo('bottom')
    screenshot('images-sandbox-batch-frontend-2')

    cy.get('a:contains("JSON data for extracted exercises")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.request(href + '&download=false').then((response) => {
          expect(response.body[0].imagesUrls.p1c1).to.match(dataUriRegex)
        })
      })

    cy.get('a:contains("JSON data for adapted exercises")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.request(href + '&download=false').then((response) => {
          expect(response.body[0].imagesUrls.p1c1).to.match(dataUriRegex)
        })
      })

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })
    cy.get('a:contains("Exercice P1Ex1")').click()
    checkImagesExport()
    screenshot('images-sandbox-batch-export')

    cy.visit('/adaptation-2')
    checkImagesFrontend(4)
    cy.wait(500) // Give time to display images
    screenshot('images-sandbox-adaptation-frontend')

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })
    checkImagesExport()
    screenshot('images-sandbox-adaptation-export')
  })

  it('extracts images in textbooks', () => {
    visit('/new-textbook')
    cy.get('[data-cy="textbook-title"]').type('Images Textbook', { delay: 0 })
    cy.get('label:contains("Single PDF") input').check()
    cy.get('input[type="file"]').eq(0).selectFile('e2e-tests/inputs/images.pdf')
    cy.get('label:contains("1-1") input[type="checkbox"]').check()
    cy.get('[data-cy="llm-name"]').eq(0).select('dummy-for-images')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-for-images')
    cy.get('button:contains("Submit")').click()
    cy.contains('in progress').should('exist')
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    cy.get('li a:contains("1")').click()
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    checkImagesFrontend(4)
    cy.wait(500) // Give time to display images
    screenshot('images-textbook-frontend')

    cy.get('a:contains("Images Textbook")').click()
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('1')
    cy.get('a:contains("Exercice 1")').invoke('removeAttr', 'target').click()
    checkImagesExport()
    screenshot('images-textbook-export')
  })

  it('can show images that are nested *and* were previously not used in an exercise (issue #184)', () => {
    if (Cypress.config('browser').name !== 'firefox' || !Cypress.config('isInteractive')) {
      // I can't understand why this test crashes Cypress *except* in interactive Firefox.
      // This is an problem because I mostly run Cypress with Electron, headless.
      return
    }

    visit('/new-extraction-batch')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/images.pdf')
    cy.get('[data-cy="llm-name"]').eq(0).select('dummy-for-images')
    cy.get('[data-cy="run-adaptation"]').select('yes')
    cy.get('[data-cy="llm-name"]').eq(1).select('dummy-for-images')
    cy.get('button:contains("Submit")').click()
    cy.contains('in progress').should('exist')
    cy.contains('in progress', { timeout: 10000 }).should('not.exist')
    cy.get('a:contains("View details")').should('have.attr', 'href', '/adaptation-2').click()

    const emptyExercise: AdaptedExercise = {
      format: 'v1',
      instruction: { lines: [] },
      statement: { pages: [] },
      example: null,
      hint: null,
      reference: null,
    }
    cy.get('[data-cy="manual-edition"]')
      .type('{selectAll}', { force: true })
      .type(JSON.stringify(emptyExercise), { delay: 0, parseSpecialCharSequences: false, force: true })
    cy.get('img').should('have.length', 1)
    cy.wait(1000)

    const exerciseWithOtherExerciseAndNestedImage: AdaptedExercise = {
      format: 'v1',
      instruction: {
        lines: [
          { contents: [{ kind: 'formatted', contents: [{ kind: 'image', identifier: 'p1c4', height: '2em' }] }] },
        ],
      },
      statement: { pages: [] },
      example: null,
      hint: null,
      reference: null,
    }
    cy.get('[data-cy="manual-edition"]')
      .type('{selectAll}', { force: true })
      .type(JSON.stringify(exerciseWithOtherExerciseAndNestedImage), {
        delay: 0,
        parseSpecialCharSequences: false,
        force: true,
      })
    cy.get('img').should('have.length', 2)
    screenshot('images-nested-frontend')

    cy.get('a:contains("standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        cy.visit(href + '&download=false')
      })

    cy.get('img').should('have.length', 2)
    screenshot('images-nested-export')
  })
})
