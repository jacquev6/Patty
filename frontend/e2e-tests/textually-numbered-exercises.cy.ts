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

import { ignoreResizeObserverLoopError, visit, loadFixtures, visitExport } from './utils'

describe('Adaptation batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-adaptation'])
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-adaptation-batch')
    cy.get('[data-cy="input-exercise-number"]').eq(0).clear().type('5')
    cy.get('[data-cy="input-page-number"]').eq(1).type('42')
    cy.get('[data-cy="input-exercise-number"]').eq(1).type('Not a number')
    cy.get('[data-cy="input-text"]').eq(1).type('Blah')
    cy.get('[data-cy="input-page-number"]').eq(2).type('42')
    cy.get('[data-cy="input-exercise-number"]').eq(2).type('6')
    cy.get('[data-cy="input-text"]').eq(2).type('Bar baz')
    cy.get('button:contains("Submit")').click()
    cy.get('h2 + p:contains("Page:")').should('have.length', 3)
    // Inputs order is preserved
    cy.get('h2 + p:contains("Page:")').eq(0).should('have.text', 'Page: 42, exercise: 5')
    cy.get('h2 + p:contains("Page:")').eq(1).should('have.text', 'Page: 42, exercise: Not a number')
    cy.get('h2 + p:contains("Page:")').eq(2).should('have.text', 'Page: 42, exercise: 6')
  })
})

describe('Classification batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-classification-batch')
    cy.get('[data-cy="input-exercise-number"]').eq(0).type('5')
    cy.get('[data-cy="input-page-number"]').eq(0).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(0).type('Instruction 5')
    cy.get('[data-cy="input-statement-text"]').eq(0).type('Statement 5')
    cy.get('[data-cy="input-exercise-number"]').eq(1).type('Not a number')
    cy.get('[data-cy="input-page-number"]').eq(1).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(1).type('Instruction Not a number')
    cy.get('[data-cy="input-statement-text"]').eq(1).type('Statement Not a number')
    cy.get('[data-cy="input-exercise-number"]').eq(2).type('6')
    cy.get('[data-cy="input-page-number"]').eq(2).type('42')
    cy.get('[data-cy="input-instruction-text"]').eq(2).type('Instruction 6')
    cy.get('[data-cy="input-statement-text"]').eq(2).type('Statement 6')
    cy.get('button:contains("Submit")').click()
    cy.get('h2 + p:contains("Page:")').should('have.length', 3)
    // Inputs order is preserved
    cy.get('h2 + p:contains("Page:")').eq(0).should('have.text', 'Page: 42, exercise: 5')
    cy.get('h2 + p:contains("Page:")').eq(1).should('have.text', 'Page: 42, exercise: Not a number')
    cy.get('h2 + p:contains("Page:")').eq(2).should('have.text', 'Page: 42, exercise: 6')
  })
})

describe('Extraction batches', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-extraction-strategy-v2'])
    ignoreResizeObserverLoopError()
  })

  it('handle textually-numbered exercises', () => {
    visit('/new-extraction-batch')
    cy.get('select').eq(2).select('dummy-for-textually-numbered-exercises')
    cy.get('select').eq(4).select('no')
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('input[type="number"]').eq(1).clear().type('1')
    cy.get('button:contains("Submit")').click()
    cy.get('h3').should('have.length', 5)
    cy.get('h3').eq(2).should('have.text', 'Exercise 5')
    cy.get('h3').eq(3).should('have.text', 'Not a number')
    cy.get('h3').eq(4).should('have.text', 'Exercise 6')
  })
})

describe('Textbooks', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures([
      'dummy-extraction-strategy-v2',
      'dummy-expression-ecrite-exercise-class',
      'dummy-transforme-mot-exercise-class',
    ])
    ignoreResizeObserverLoopError()
  })

  it('handles textually-numbered extracted exercises', () => {
    visit('/new-textbook')
    cy.get('[data-cy="textbook-title"]').type('Title')
    cy.get('label:contains("Single PDF") input').check()
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('label:contains("1-2") input').check()
    cy.get('select').eq(2).select('dummy-for-textually-numbered-exercises')
    cy.get('button:contains("Submit")').click()
    cy.get('li a:contains("1")').click()
    cy.get('h2').should('have.length', 3)
    cy.get('h2').eq(0).should('contain', 'Exercise 5')
    cy.get('h2').eq(1).should('contain', 'Not a number')
    cy.get('h2').eq(2).should('contain', 'Exercise 6')

    cy.get('button:contains("Approve")', { timeout: 10000 }).should('have.length', 3)
    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('1')
    cy.get('div.exercise').eq(0).should('contain.text', 'Not a number')
    cy.get('div.exercise').eq(1).should('contain.text', 'Exercice 5')
    cy.get('div.exercise').eq(2).should('contain.text', 'Exercice 6')
  })

  it('handles textually-numbered external exercises', () => {
    visit('/new-textbook')
    cy.get('[data-cy="textbook-title"]').type('Title')
    cy.get('label:contains("Multiple PDFs") input').check()
    cy.get('button:contains("Submit")').click()
    cy.get("input[data-cy='external-files']").selectFile([
      'e2e-tests/inputs/P40ExDéfi Langue.docx',
      "e2e-tests/inputs/P40ExJ'écris.docx",
      'e2e-tests/inputs/P40ExÀ toi de jouer.xlsx',
    ])
    cy.get('li:contains("40")').should('exist')

    visitExport('/api/export/textbook/1.html')
    cy.get('[data-cy="page-number-filter"]').type('40')
    cy.get('div.exercise').eq(0).should('contain.text', 'Défi Langue - Word')
    cy.get('div.exercise').eq(1).should('contain.text', "J'écris - Word")
    cy.get('div.exercise').eq(2).should('contain.text', 'À toi de jouer - Excel')
    cy.get('div.exercise').eq(3).should('not.be.visible')
  })

  it('handle textually-numbered manual exercises', () => {
    visit('/new-textbook')
    cy.get('[data-cy="textbook-title"]').type('Title')
    cy.get('label:contains("Multiple PDFs") input').check()
    cy.get('button:contains("Submit")').click()
    cy.visit('/textbook-1/page-42/new-adaptations')
    cy.get('[data-cy="input-exercise-number"]').clear().type('Blah blah')
    cy.get('[data-cy="input-exercise-class"]').select('TransformeMot')
    cy.get('[data-cy="input-text"]').type('This is a manually-added exercise.', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/textbook-1/page-42')
    cy.get('div.busy', { timeout: 10000 }).should('not.exist')
    cy.get('h2:contains("Blah blah: TransformeMot")').should('exist')
  })
})
