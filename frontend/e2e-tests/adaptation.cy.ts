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
import { ignoreResizeObserverLoopError, loadFixtures, screenshot, visit } from './utils'

describe('The adaptation batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['dummy-adaptation'])
    ignoreResizeObserverLoopError()
    visit('/new-adaptation-batch')
  })

  it('looks like this', () => {
    screenshot('adaptation-batch-creation-page')
  })

  it('lets user add and remove input exercises', () => {
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('button:contains("Submit")').should('be.enabled')
    cy.get('@input-text').should('have.length', 2)
    cy.get('@input-text')
      .eq(0)
      .should(
        'have.value',
        'Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n',
      )
    cy.get('@input-text').eq(1).should('have.value', '').type('Blah blah blah.', { delay: 0 })
    cy.get('@input-text').should('have.length', 3)
    cy.get('@input-text').eq(2).should('have.value', '').type('Bleh bleh bleh.', { delay: 0 })
    cy.get('@input-text').should('have.length', 4)
    cy.get('@input-text').eq(3).should('have.value', '').type('Blih blih blih.', { delay: 0 })
    cy.get('@input-text').should('have.length', 5)
    cy.get('@input-text').eq(3).type('{selectAll}{del}')
    cy.get('@input-text').should('have.length', 4)
    cy.get('@input-text').eq(3).should('have.focus')
    cy.get('@input-text').eq(1).type('{selectAll}{del}')
    cy.get('@input-text').should('have.length', 4)
    cy.get('@input-text').eq(1).should('have.focus')
    cy.get('@input-text').eq(2).type('{selectAll}{del}')
    cy.get('@input-text').should('have.length', 2)
    cy.get('@input-text').eq(1).should('have.focus')
    cy.get('@input-text').eq(0).type('{selectAll}{del}')
    cy.get('@input-text').should('have.length', 1)
    cy.get('button:contains("Submit")').should('be.disabled')
  })

  it('remembers the last LLM model used', () => {
    cy.get('[data-cy="llm-name"]').as('llm-name')

    cy.get('@llm-name').should('have.value', 'dummy-1')
    cy.get('@llm-name').select('dummy-2')
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@llm-name').should('have.value', 'dummy-2')
  })

  it('remembers the last system prompt used', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')

    cy.get('@system-prompt').type(' Blih blih.', { delay: 0 })
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
  })

  it('remembers the last "allow choice in instruction" used', () => {
    cy.get('[data-cy="allow-choice-in-instruction"]').as('allow-choice-in-instruction')

    cy.get('@allow-choice-in-instruction').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@allow-choice-in-instruction').should('not.be.checked')
  })

  it('remembers the last "allow free text input in statement" used', () => {
    cy.get('[data-cy="allow-free-text-input-in-statement"]').as('allow-free-text-input-in-statement')

    cy.get('@allow-free-text-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@allow-free-text-input-in-statement').should('not.be.checked')
  })

  it('remembers the last "allow multiple choices input in statement" used', () => {
    cy.get('[data-cy="allow-multiple-choices-input-in-statement"]').as('allow-multiple-choices-input-in-statement')

    cy.get('@allow-multiple-choices-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@allow-multiple-choices-input-in-statement').should('not.be.checked')
  })

  it('remembers the last "allow selectable input in statement" used', () => {
    cy.get('[data-cy="allow-selectable-input-in-statement"]').as('allow-selectable-input-in-statement')

    cy.get('@allow-selectable-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@allow-selectable-input-in-statement').should('not.be.checked')
  })

  it('remembers the last inputs used', () => {
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('@input-text').should('have.length', 2)
    cy.get('@input-text').eq(0).type('{selectAll}Blah blah.', { delay: 0 })
    cy.get('@input-text').eq(1).type('{selectAll}Bleh bleh.', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@input-text').should('have.length', 3)
    cy.get('@input-text').eq(0).should('have.value', 'Blah blah.')
    cy.get('@input-text').eq(1).should('have.value', 'Bleh bleh.')
  })

  it('remembers separately the last strategy and inputs used by each user', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('@system-prompt').should('have.value', 'Blah blah blah.')
    cy.get('@input-text')
      .eq(0)
      .should(
        'have.value',
        'Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n',
      )
    cy.get('@system-prompt').type("{selectAll}Alice's prompt.", { delay: 0 })
    cy.get('@input-text').eq(0).type("{selectAll}Alice's input.", { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@system-prompt').should('have.value', "Alice's prompt.")
    cy.get('@input-text').eq(0).should('have.value', "Alice's input.")
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Bob', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('@system-prompt').should('have.value', 'Blah blah blah.')
    cy.get('@input-text')
      .eq(0)
      .should(
        'have.value',
        'Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n',
      )
    cy.get('@system-prompt').type("{selectAll}Bob's prompt.", { delay: 0 })
    cy.get('@input-text').eq(0).type("{selectAll}Bob's input.", { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Bob")').should('exist')

    cy.visit('/new-adaptation-batch')
    cy.get('@system-prompt').should('have.value', "Bob's prompt.")
    cy.get('@input-text').eq(0).should('have.value', "Bob's input.")
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('@system-prompt').should('have.value', "Alice's prompt.")
    cy.get('@input-text').eq(0).should('have.value', "Alice's input.")
  })

  it('submits an adaptation batch and refreshes until it is ready', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Sleep 2', { delay: 0 })

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('button:contains("View details")').should('be.disabled')
    cy.get('button:contains("View details")', { timeout: 10000 }).should('be.enabled')

    cy.visit('/adaptation-1')
    cy.get('a:contains("Adaptation batch 1")').should('have.attr', 'href', '/adaptation-batch-1')
  })

  it('handles non-JSON response from the LLM', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Not JSON', { delay: 0 })

    cy.get('button:contains("Submit")').click()

    cy.get('h2:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("The LLM returned a response that is not correct JSON.")').should('exist')
  })

  it('handles invalid JSON response from the LLM', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Invalid JSON', { delay: 0 })

    cy.get('button:contains("Submit")').click()

    cy.get('h2:contains("Error with the LLM")').should('exist')
    cy.get(
      'p:contains("The LLM returned a JSON response that does not validate against the adapted exercise schema.")',
    ).should('exist')
  })

  it('handles unknown error from the LLM', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Unknown error', { delay: 0 })

    cy.get('button:contains("Submit")').click()

    cy.get('h2:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("The LLM caused an unknown error.")').should('exist')
  })

  it('opens several text files as inputs', () => {
    cy.get('[data-cy="input-text"]').as('input-text')
    cy.get('[data-cy="input-page-number"]').as('input-page-number')
    cy.get('[data-cy="input-exercise-number"]').as('input-exercise-number')

    cy.get("input[data-cy='input-files']").selectFile([
      // Lexicographical order is inappropriate because files have numbers in their names.
      'e2e-tests/inputs/P16Ex4.txt',
      'e2e-tests/inputs/P6Ex14.txt',
      'e2e-tests/inputs/P6Ex8.txt',
    ])
    cy.get('@input-text').should('have.length', 4)
    // Inputs are sorted by page and exercise number.
    cy.get('h2:contains("Input 1") > span.discreet:contains("P6Ex8.txt")').should('exist')
    cy.get('@input-page-number').eq(0).should('have.value', 6)
    cy.get('@input-exercise-number').eq(0).should('have.value', '8')
    cy.get('@input-text')
      .eq(0)
      .should(
        'have.value',
        'Complète avec "le soleil" ou "la voiture"\na. Le lit du chat est réchauffé par ...\nb. Le bruit de ... a réveillé le chien.\n',
      )
    cy.get('h2:contains("Input 2") > span.discreet:contains("P6Ex14.txt")').should('exist')
    cy.get('@input-page-number').eq(1).should('have.value', 6)
    cy.get('@input-exercise-number').eq(1).should('have.value', '14')
    cy.get('@input-text')
      .eq(1)
      .should(
        'have.value',
        'Complète avec "les chats" ou "les chiens"\na. Les souris sont chassées par ...\nb. Les chats sont chassés par ...\n',
      )
    cy.get('h2:contains("Input 3") > span.discreet:contains("P16Ex4.txt")').should('exist')
    cy.get('@input-page-number').eq(2).should('have.value', 16)
    cy.get('@input-exercise-number').eq(2).should('have.value', '4')
    cy.get('@input-text')
      .eq(2)
      .should(
        'have.value',
        'Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n',
      )
    cy.get('h2:contains("Input 4") > span.discreet:contains("empty")').should('exist')
    cy.get('@input-page-number').eq(3).should('have.value', '')
    cy.get('@input-exercise-number').eq(3).should('have.value', '')
    cy.get('@input-text').eq(3).should('have.value', '')

    cy.get('h2:contains("Input 2")').find('span.discreet:contains("P6Ex14.txt")').should('exist')
    cy.get('@input-text').eq(1).type('{backspace}')
    cy.get('h2:contains("Input 2")').find('span.discreet:contains("P6Ex14.txt")').should('not.exist')

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
  })

  it('opens several text files as inputs', () => {
    cy.get('[data-cy="input-text"]').as('input-text')
    cy.get('[data-cy="input-page-number"]').as('input-page-number')
    cy.get('[data-cy="input-exercise-number"]').as('input-exercise-number')

    cy.get("input[data-cy='input-files']").selectFile('e2e-tests/inputs/test.zip')
    cy.get('@input-text').should('have.length', 4)
    // Inputs are sorted by page and exercise number.
    cy.get('h2:contains("Input 1") > span.discreet:contains("P6Ex8.txt in test.zip")').should('exist')
    cy.get('@input-page-number').eq(0).should('have.value', 6)
    cy.get('@input-exercise-number').eq(0).should('have.value', '8')
    cy.get('@input-text')
      .eq(0)
      .should(
        'have.value',
        'Complète avec "le soleil" ou "la voiture"\na. Le lit du chat est réchauffé par ...\nb. Le bruit de ... a réveillé le chien.\n',
      )
    cy.get('h2:contains("Input 2") > span.discreet:contains("P6Ex14.txt in test.zip")').should('exist')
    cy.get('@input-page-number').eq(1).should('have.value', 6)
    cy.get('@input-exercise-number').eq(1).should('have.value', '14')
    cy.get('@input-text')
      .eq(1)
      .should(
        'have.value',
        'Complète avec "les chats" ou "les chiens"\na. Les souris sont chassées par ...\nb. Les chats sont chassés par ...\n',
      )
    cy.get('h2:contains("Input 3") > span.discreet:contains("P16Ex4.txt in test.zip")').should('exist')
    cy.get('@input-page-number').eq(2).should('have.value', 16)
    cy.get('@input-exercise-number').eq(2).should('have.value', '4')
    cy.get('@input-text')
      .eq(2)
      .should(
        'have.value',
        'Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n',
      )
    cy.get('h2:contains("Input 4") > span.discreet:contains("empty")').should('exist')
    cy.get('@input-page-number').eq(3).should('have.value', '')
    cy.get('@input-exercise-number').eq(3).should('have.value', '')
    cy.get('@input-text').eq(3).should('have.value', '')
  })

  it('saves and loads settings by name', () => {
    cy.get('[data-cy="settings-name"]').as('settings-name')
    cy.get('[data-cy="system-prompt"]').as('system-prompt')

    // Create from scratch
    cy.get('@settings-name').should('have.value', '')
    cy.get('@settings-name').focus()
    cy.get('[data-cy="suggestion"]').should('have.length', 0)
    cy.get('@settings-name').type('Alpha', { delay: 0 })

    cy.get('@system-prompt').type('{selectAll}Prompt alpha 1', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')

    // Create from existing
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 1')
    cy.get('@settings-name').type('{selectAll}{del}', { delay: 0 })
    cy.get('@system-prompt').type('{selectAll}Not prompt', { delay: 0 })
    cy.get('@settings-name').focus()
    cy.get('[data-cy="suggestion"]').as('suggestions')
    cy.get('@suggestions').should('have.length', 1)
    cy.get('@suggestions').eq(0).should('have.text', 'Alpha').click()
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 1')

    cy.get('@system-prompt').type('{selectAll}Prompt alpha 2', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')

    // Create from latest version
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 2')
    cy.get('@settings-name').focus()
    cy.get('@suggestions').should('have.length', 2)
    cy.get('@suggestions').eq(1).should('have.text', 'Alpha (previous version)').click()
    cy.get('@settings-name').should('have.value', 'Alpha (previous version)')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 1')
    cy.get('@settings-name').type('{selectAll}{del}', { delay: 0 })
    cy.get('@suggestions').eq(0).should('have.text', 'Alpha').click()
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 2')

    cy.get('@system-prompt').type('{selectAll}Prompt alpha 3 (bad)', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-4')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3 (bad)')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')
    cy.visit('/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')

    // Restore previous version
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 3 (bad)')
    cy.get('@settings-name').focus()
    cy.get('@suggestions').should('have.length', 2)
    cy.get('@suggestions').eq(0).should('have.text', 'Alpha')
    cy.get('@suggestions').eq(1).should('have.text', 'Alpha (previous version)').click()
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 2')
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-5')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)') // Previous version again
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')
    cy.visit('/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha') // Current version again
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-4')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3 (bad)')

    // Create from latest version
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 2')
    cy.get('@settings-name').focus()
    cy.get('@suggestions').should('have.length', 2)
    cy.get('@suggestions').eq(0).should('have.text', 'Alpha')
    cy.get('@suggestions').eq(1).should('have.text', 'Alpha (previous version)')
    cy.get('@system-prompt').type('{selectAll}Prompt alpha 3bis (bad)', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-6')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3bis (bad)')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')
    cy.visit('/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-4')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3 (bad)')
    cy.visit('/adaptation-batch-5')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')

    // Create from previous version
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 3bis (bad)')
    cy.get('@settings-name').focus()
    cy.get('@suggestions').should('have.length', 2)
    cy.get('@suggestions').eq(0).should('have.text', 'Alpha')
    cy.get('@suggestions').eq(1).should('have.text', 'Alpha (previous version)').click()
    cy.get('@settings-name').should('have.value', 'Alpha (previous version)')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 2')
    cy.get('@system-prompt').type('{selectAll}Prompt alpha 3ter (good)', { delay: 0 })
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-7')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3ter (good)')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')
    cy.visit('/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-4')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3 (bad)')
    cy.visit('/adaptation-batch-5')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-6')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3bis (bad)')

    // Create without changing strategy
    cy.visit('/new-adaptation-batch')
    cy.get('@settings-name').should('have.value', 'Alpha')
    cy.get('@system-prompt').should('have.value', 'Prompt alpha 3ter (good)')
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('equal', '/adaptation-batch-8')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3ter (good)')

    cy.visit('/adaptation-batch-2')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 1')
    cy.visit('/adaptation-batch-3')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-4')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3 (bad)')
    cy.visit('/adaptation-batch-5')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (previous version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 2')
    cy.visit('/adaptation-batch-6')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha (older version)')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3bis (bad)')
    cy.visit('/adaptation-batch-7')
    cy.get('p:contains("Name:")').should('have.text', 'Name: Alpha')
    cy.get('p:contains("Prompt")').should('have.text', 'Prompt alpha 3ter (good)')
  })

  it('uses its base batch to initialize the form', () => {
    loadFixtures(['20-adaptation-batches'])
    cy.visit('/new-adaptation-batch?base=8')
    cy.get('[data-cy="system-prompt"]').should('have.value', 'Blah blah blah 8.')
    cy.visit('/new-adaptation-batch?base=14')
    cy.get('[data-cy="system-prompt"]').should('have.value', 'Blah blah blah 14.')
    cy.visit('/new-adaptation-batch') // Uses batch 1 because Alice has never created a batch
    cy.get('[data-cy="system-prompt"]').should('have.value', 'Blah blah blah 1.')
  })

  it('reproduces issue #59', () => {
    // @todo Investigate why this test fails *only* on Firefox.
    if (Cypress.browser.name === 'firefox') {
      return
    }

    cy.get('[data-cy="settings-name"]').type('Blah')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah Alice 1')
    cy.get('button:contains("Submit")').click()

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Bob', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('[data-cy="settings-name"]').type('Blah')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah Bob 1')
    cy.get('button:contains("Submit")').click()
    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah Bob 2')
    cy.get('button:contains("Submit")').click()

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('[data-cy="settings-name"]').should('have.value', 'Blah (older version)') // Because Alice's last batch was submitted with the older version
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Name: Blah")').should('exist') // Older version became current (similar to how previous version can become current)

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="settings-name"]').focus()
    cy.get('.suggestion').should('have.length', 2)
    cy.get('.suggestion').eq(0).should('have.text', 'Blah')
    cy.get('.suggestion').eq(1).should('have.text', 'Blah (previous version)')
  })

  it('reproduces issue #87', () => {
    // @todo Investigate why this test fails *only* on Firefox.
    if (Cypress.browser.name === 'firefox') {
      return
    }

    cy.get('[data-cy="settings-name"]').type('Blah')
    cy.get('[data-cy="settings-name"]').type('{selectAll}{backspace}')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah 1')
    cy.get('button:contains("Submit")').click()

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah 2')
    cy.get('button:contains("Submit")').click()

    cy.visit('/new-adaptation-batch')
    cy.get('[data-cy="system-prompt"]').type('{selectAll}Blah 3')
    cy.get('button:contains("Submit")').click()

    cy.visit('/')
    cy.get(':contains("previous version")').should('not.exist')
    cy.get(':contains("older version")').should('not.exist')
  })
})

describe('The adaptation batch edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
    ignoreResizeObserverLoopError()
  })

  it('displays "Not found" when the adaptation batch does not exist', () => {
    visit('/adaptation-batch-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('displays "Not found" when the adaptation batch id is not an integer', () => {
    visit('/adaptation-batch-nope')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('looks like this', () => {
    visit('/adaptation-batch-1')

    cy.get('h1:contains("Strategy")').should('exist')

    screenshot('adaptation-batch-edition-page.1')

    cy.get('button:contains("Full screen")').eq(0).click()

    screenshot('adaptation-batch-edition-page.2')
  })

  it('does not remember answers', () => {
    visit('/adaptation-batch-1')

    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/adaptation-batch-1')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
  })

  it('has a link to create a new batch based on it', () => {
    visit('/adaptation-batch-1')

    cy.get('a:contains("New batch based on this one")').should('have.attr', 'href', '/new-adaptation-batch?base=1')
  })
})

describe('The adaptation edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
    ignoreResizeObserverLoopError()
  })

  it('displays "Not found" when the adaptation does not exist', () => {
    visit('/adaptation-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('displays "Not found" when the adaptation id is not an integer', () => {
    visit('/adaptation-nope')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('has a link to its adaptation batch', () => {
    visit('/adaptation-1')

    cy.get('a:contains("Adaptation batch 1")').should('have.attr', 'href', '/adaptation-batch-1')
  })

  it('allows manual JSON without optional fields', () => {
    visit('/adaptation-1')
    // No attribute "reducedLineSpacing" in the multiple-choices input
    cy.get('[data-cy="manual-edition"]')
      .clear({ force: true })
      .type(
        '{"format": "v1","instruction": {"lines": []},"example": null,"hint": null,"statement": {"pages": [{"lines": [{"contents": [{"kind": "multipleChoicesInput","choices": [{"contents": [{"kind": "text", "text": "alpha"}]},{"contents": [{"kind": "text", "text": "bravo"}]}],"showChoicesByDefault": false}]}]}]},"reference": null}',
        { delay: 0, parseSpecialCharSequences: false },
      )
    cy.get('button[data-cy="reformat-manual-edition"]').should('be.enabled')
    cy.get('span.tricolorable:contains("....")').should('exist')
  })

  it('does not reproduce issue #181', () => {
    visit('/adaptation-1')

    const exerciseBefore: AdaptedExercise = {
      format: 'v1',
      instruction: {
        lines: [],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  {
                    kind: 'multipleChoicesInput',
                    choices: [
                      {
                        contents: [{ kind: 'text', text: 'alpha' }],
                      },
                      {
                        contents: [{ kind: 'text', text: 'bravo' }],
                      },
                    ],
                    showChoicesByDefault: false,
                    reducedLineSpacing: false,
                  },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    }

    cy.get('[data-cy="manual-edition"]')
      .clear({ force: true })
      .type(JSON.stringify(exerciseBefore), { delay: 0, parseSpecialCharSequences: false, force: true })

    cy.get('[data-cy="multipleChoicesInput"]').click()
    cy.get('[data-cy="choice0"]').click()

    const exerciseAfter: AdaptedExercise = {
      format: 'v1',
      instruction: {
        lines: [],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [{ kind: 'freeTextInput' }],
              },
            ],
          },
        ],
      },
      reference: null,
    }

    cy.get('[data-cy="manual-edition"]')
      .type('{selectAll}', { force: true })
      .type(JSON.stringify(exerciseAfter), { delay: 0, parseSpecialCharSequences: false, force: true })

    cy.wait(100)
    cy.get('h1:contains("There was a bug")').should('not.exist')
  })
})

function setUpAliases() {
  cy.get('[data-cy="user-prompt"]').as('user-prompt')
  cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')

  cy.get('[data-cy="manual-edition"]').as('manual-edition')
  cy.get('button[data-cy="reset-manual-edition"]').as('reset-manual-edition')
  cy.get('button[data-cy="reformat-manual-edition"]').as('reformat-manual-edition')
}

function submitAdjustment(prompt: string) {
  cy.get('@user-prompt').type('{selectAll}' + prompt, { delay: 0 })
  cy.get('@submit-adjustment').click()
  cy.get('@user-prompt').should('have.value', '')
  cy.get(`div.user-prompt:contains("${prompt}")`).should('exist')
  cy.get(`div.user-prompt:contains("${prompt}")`).find('div:contains("❌")').should('exist')
}

function rewindAdjustment() {
  cy.get('div:contains("❌")').last().click()
}

const validExercise = {
  unformattedJson:
    '{"format":"v1","instruction":{"lines":[{"contents":[{"kind":"text","text":"Blah"}]}]},"example":null,"hint":null,"statement":{"pages":[]},"reference":null}',
  formattedJson:
    '{\n  "format": "v1",\n  "instruction": {"lines": [{"contents": [{"kind": "text", "text": "Blah"}]}]},\n  "example": null,\n  "hint": null,\n  "statement": {"pages": []},\n  "reference": null\n}',
}

function fixJsonManually() {
  cy.get('@manual-edition')
    .type('{selectAll}', { force: true })
    .type(validExercise.unformattedJson, { delay: 0, parseSpecialCharSequences: false, force: true })
}

function invalidateJsonManually() {
  cy.get('@manual-edition')
    .type('{selectAll}', { force: true })
    .type('{}', { delay: 0, parseSpecialCharSequences: false, force: true })
}

function breakJsonManually() {
  cy.get('@manual-edition').type('{selectAll}Not JSON.', { delay: 0, force: true })
}

function shouldBeSuccess() {
  cy.get('h1:contains("Error with the LLM")').should('not.exist')
  cy.get('h1:contains("Error in manually edited")').should('not.exist')
  cy.get('h1:contains("Adapted exercise")').should('exist')
}

function shouldBeLlmInvalidJson() {
  cy.get('h1:contains("Error with the LLM")').should('exist')
  cy.get(
    'p:contains("The LLM returned a JSON response that does not validate against the adapted exercise schema.")',
  ).should('exist')
  cy.get('h1:contains("Error in manually edited")').should('not.exist')
  cy.get('h1:contains("Adapted exercise")').should('not.exist')
  cy.get('@manual-edition').should('have.value', '{}')
}

function shouldBeManualInvalidJson() {
  cy.get('h1:contains("Error with the LLM")').should('not.exist')
  cy.get('h1:contains("Error in manually edited")').should('exist')
  cy.get('h2:contains("Validation errors")').should('exist')
  cy.get('h1:contains("Adapted exercise")').should('not.exist')
}

function shouldBeLlmNotJson() {
  cy.get('h1:contains("Error with the LLM")').should('exist')
  cy.get('p:contains("The LLM returned a response that is not correct JSON.")').should('exist')
  cy.get('h1:contains("Error in manually edited")').should('not.exist')
  cy.get('h1:contains("Adapted exercise")').should('not.exist')
  cy.get('@manual-edition').should('have.value', 'This is not JSON.')
}

function shouldBeManualNotJson() {
  cy.get('h1:contains("Error with the LLM")').should('not.exist')
  cy.get('h1:contains("Error in manually edited")').should('exist')
  cy.get('h2:contains("Syntax error")').should('exist')
  cy.get('h1:contains("Adapted exercise")').should('not.exist')
}

function shouldAllowAdjustment() {
  cy.get('@user-prompt').should('be.enabled')
}

function shouldForbidAdjustment() {
  cy.get('@user-prompt').should('be.disabled')
  cy.get('@submit-adjustment').should('be.disabled')
}

describe('The edition page for an initially successful adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
    ignoreResizeObserverLoopError()
    visit('/adaptation-1')
    setUpAliases()
    shouldBeSuccess()
    shouldAllowAdjustment()
  })

  it('looks like this', () => {
    screenshot('adaptation-edition-page.success')
  })

  it('reformats, saves and resets manual edits', () => {
    fixJsonManually()
    cy.get('@manual-edition').should('have.value', validExercise.unformattedJson)
    cy.get('@reformat-manual-edition').click()
    cy.get('@manual-edition').should('have.value', validExercise.formattedJson)
    shouldBeSuccess()
    shouldForbidAdjustment()

    cy.visit('/adaptation-1')
    cy.get('@manual-edition').should('have.value', validExercise.formattedJson)
    cy.get('@reset-manual-edition').click()
    shouldBeSuccess()
    shouldAllowAdjustment()
  })

  it('does not remember answers', () => {
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/adaptation-1')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
  })

  it('enables the "submit adjustment" button', () => {
    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
    cy.get('@user-prompt').type('Blah.', { delay: 0 })
    cy.get('@user-prompt').should('have.value', 'Blah.')
    cy.get('@submit-adjustment').should('be.enabled')
    cy.get('@user-prompt').type('{selectAll}{del}', { delay: 0 })
    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
  })

  it('submits and rewinds successful adjustments', () => {
    cy.get('@user-prompt').type('Blah.', { delay: 0 })
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist')
    shouldBeSuccess()
    shouldAllowAdjustment()
    cy.get('@user-prompt').type('Bleh.', { delay: 0 })
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('not.exist')
    cy.get('div.user-prompt:contains("Bleh.")').should('exist')
    shouldBeSuccess()
    shouldAllowAdjustment()
    cy.get('div.user-prompt:contains("Bleh.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Bleh.")').should('not.exist')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    shouldBeSuccess()
    shouldAllowAdjustment()
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Blah.")').should('not.exist')
    shouldBeSuccess()
    shouldAllowAdjustment()
  })

  it('submit and rewinds non-JSON adjustment', () => {
    submitAdjustment('Not JSON')
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeSuccess()
    shouldAllowAdjustment()
  })

  it('submit and rewinds invalid-JSON adjustment', () => {
    submitAdjustment('Invalid JSON')
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeSuccess()
    shouldAllowAdjustment()
  })

  it('invalidates the JSON manually', () => {
    invalidateJsonManually()
    shouldBeManualInvalidJson()
    shouldForbidAdjustment()
    screenshot('adaptation-edition-page.manual-invalid')
  })

  it('breaks the JSON manually', () => {
    breakJsonManually()
    shouldBeManualNotJson()
    shouldForbidAdjustment()
    screenshot('adaptation-edition-page.manual-not-json')
  })

  it('does not reproduce issue #96', () => {
    cy.get('@manual-edition').type('{selectAll}', { force: true })
    cy.get('@manual-edition').type(
      '{"format":"v1","instruction":{"lines":[{"contents":[{"kind":"text","text":"Blah"}]}]},"example":null,"hint":null,"statement":{"pages":[{"lines": [{"contents":[{"kind": "text", "text": "Page1"}]}]},',
      { delay: 0, parseSpecialCharSequences: false, force: true },
    )
    cy.get('@manual-edition').type(
      '{"lines": [{"contents":[{"kind": "text", "text": "Page2"}]}]},{"lines": [{"contents":[{"kind": "text", "text": "Page3"}]}]}]},"reference":null}',
      { delay: 0, parseSpecialCharSequences: false, force: true },
    )
    cy.get('.control').eq(1).click().click()
    cy.get('span:contains("Page3")').should('exist')
    cy.get('@manual-edition')
      .type('{selectAll}', { force: true })
      .type(
        '{"format":"v1","instruction":{"lines":[{"contents":[{"kind":"text","text":"Blah"}]}]},"example":null,"hint":null,"statement":{"pages":[{"lines": [{"contents":[{"kind": "text", "text": "PageA"}]}]},{"lines": [{"contents":[{"kind": "text", "text": "PageB"}]}]}]},"reference":null}',
        { delay: 0, parseSpecialCharSequences: false, force: true },
      )
    cy.get('span:contains("PageB")').should('exist')
    cy.get('h1:contains("There was a bug")').should('not.exist')
    cy.get(':contains("TypeError")').should('not.exist')
  })

  it('shows a message when the LLM quota is exceeded', () => {
    cy.get('@user-prompt').type('Retryable error', { delay: 0 })
    cy.get('@submit-adjustment').click()
    cy.get('p:contains("Adjustment failed. Please try again later.")').should('exist')
    cy.get('@user-prompt').should('have.value', 'Retryable error')
  })
})

describe('The edition page for an initially invalid-json adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
    ignoreResizeObserverLoopError()
    visit('/adaptation-3')
    setUpAliases()
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
  })

  it('looks like this', () => {
    screenshot('adaptation-edition-page.invalid-json')
  })

  it('submit and rewinds successful adjustment', () => {
    submitAdjustment('Blah')
    shouldBeSuccess()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
  })

  it('submit and rewinds non-JSON adjustment', () => {
    submitAdjustment('Not JSON')
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
  })

  it('submit and rewinds invalid-JSON adjustment', () => {
    submitAdjustment('Invalid JSON')
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
  })

  it('fixes the JSON manually', () => {
    fixJsonManually()
    shouldBeSuccess()
    shouldForbidAdjustment()
  })

  it('invalidates the JSON manually', () => {
    invalidateJsonManually()
    shouldBeManualInvalidJson()
    shouldForbidAdjustment()
  })

  it('breaks the JSON manually', () => {
    breakJsonManually()
    shouldBeManualNotJson()
    shouldForbidAdjustment()
  })
})

describe('The edition page for an initially not-json adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    loadFixtures(['mixed-dummy-adaptation-batch'])
    ignoreResizeObserverLoopError()
    visit('/adaptation-4')
    setUpAliases()
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
  })

  it('looks like this', () => {
    screenshot('adaptation-edition-page.not-json')
  })

  it('submit and rewinds successful adjustment', () => {
    submitAdjustment('Blah')
    shouldBeSuccess()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
  })

  it('submit and rewinds non-JSON adjustment', () => {
    submitAdjustment('Not JSON')
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
  })

  it('submit and rewinds invalid-JSON adjustment', () => {
    submitAdjustment('Invalid JSON')
    shouldBeLlmInvalidJson()
    shouldAllowAdjustment()
    rewindAdjustment()
    shouldBeLlmNotJson()
    shouldAllowAdjustment()
  })

  it('fixes the JSON manually', () => {
    fixJsonManually()
    shouldBeSuccess()
    shouldForbidAdjustment()
  })

  it('invalidates the JSON manually', () => {
    invalidateJsonManually()
    shouldBeManualInvalidJson()
    shouldForbidAdjustment()
  })

  it('breaks the JSON manually', () => {
    breakJsonManually()
    shouldBeManualNotJson()
    shouldForbidAdjustment()
  })
})
