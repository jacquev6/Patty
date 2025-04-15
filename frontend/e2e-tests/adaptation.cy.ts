describe('The batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')

    Cypress.on('uncaught:exception', error => {
      if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
        // @todo Deep dive into this issue: avoid the error instead of ignoring it.
        // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
        return false
      } else {
        return true
      }
    })

    cy.visit('/new-batch')

    cy.get('[data-cy="identified-user"]').type('Alice', {delay: 0})
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('looks like this', () => {
    cy.compareSnapshot(`batch-creation-page.${Cypress.browser.name}`)
  })

  it('lets user add and remove input exercises', () => {
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('button:contains("Submit")').should('be.enabled')
    cy.get('@input-text').should('have.length', 2)
    cy.get('@input-text').eq(0).should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n')
    cy.get('@input-text').eq(1).should('have.value', '').type('Blah blah blah.', {delay: 0})
    cy.get('@input-text').should('have.length', 3)
    cy.get('@input-text').eq(2).should('have.value', '').type('Bleh bleh bleh.', {delay: 0})
    cy.get('@input-text').should('have.length', 4)
    cy.get('@input-text').eq(3).should('have.value', '').type('Blih blih blih.', {delay: 0})
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

    cy.visit('/new-batch')
    cy.get('@llm-name').should('have.value', 'dummy-2')
  })

  it('remembers the last system prompt used', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')

    cy.get('@system-prompt').type(' Blih blih.', {delay: 0})
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@system-prompt').should('have.value', 'Blah blah blah. Blih blih.')
  })

  it('remembers the last "allow choice in instruction" used', () => {
    cy.get('[data-cy="allow-choice-in-instruction"]').as('allow-choice-in-instruction')

    cy.get('@allow-choice-in-instruction').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@allow-choice-in-instruction').should('not.be.checked')
  })

  it('remembers the last "allow arrow in statement" used', () => {
    cy.get('[data-cy="allow-arrow-in-statement"]').as('allow-arrow-in-statement')

    cy.get('@allow-arrow-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@allow-arrow-in-statement').should('not.be.checked')
  })

  it('remembers the last "allow free text input in statement" used', () => {
    cy.get('[data-cy="allow-free-text-input-in-statement"]').as('allow-free-text-input-in-statement')

    cy.get('@allow-free-text-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@allow-free-text-input-in-statement').should('not.be.checked')
  })

  it('remembers the last "allow multiple choices input in statement" used', () => {
    cy.get('[data-cy="allow-multiple-choices-input-in-statement"]').as('allow-multiple-choices-input-in-statement')

    cy.get('@allow-multiple-choices-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@allow-multiple-choices-input-in-statement').should('not.be.checked')
  })

  it('remembers the last "allow selectable input in statement" used', () => {
    cy.get('[data-cy="allow-selectable-input-in-statement"]').as('allow-selectable-input-in-statement')

    cy.get('@allow-selectable-input-in-statement').should('be.checked').uncheck()

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@allow-selectable-input-in-statement').should('not.be.checked')
  })

  it('remembers the last inputs used', () => {
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('@input-text').should('have.length', 2)
    cy.get('@input-text').eq(0).type('{selectAll}Blah blah.', {delay: 0})
    cy.get('@input-text').eq(1).type('{selectAll}Bleh bleh.', {delay: 0})
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@input-text').should('have.length', 3)
    cy.get('@input-text').eq(0).should('have.value', 'Blah blah.')
    cy.get('@input-text').eq(1).should('have.value', 'Bleh bleh.')
  })

  it('remembers separately the last strategy and inputs used by each user', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')
    cy.get('[data-cy="input-text"]').as('input-text')

    cy.get('@system-prompt').should('have.value', 'Blah blah blah.')
    cy.get('@input-text').eq(0).should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n')
    cy.get('@system-prompt').type('{selectAll}Alice\'s prompt.', {delay: 0})
    cy.get('@input-text').eq(0).type('{selectAll}Alice\'s input.', {delay: 0})
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')

    cy.visit('/new-batch')
    cy.get('@system-prompt').should('have.value', 'Alice\'s prompt.')
    cy.get('@input-text').eq(0).should('have.value', 'Alice\'s input.')
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Bob', {delay: 0})
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('@system-prompt').should('have.value', 'Blah blah blah.')
    cy.get('@input-text').eq(0).should('have.value', '5 Complète avec "le vent" ou "la pluie"\na. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...\n')
    cy.get('@system-prompt').type('{selectAll}Bob\'s prompt.', {delay: 0})
    cy.get('@input-text').eq(0).type('{selectAll}Bob\'s input.', {delay: 0})
    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Bob")').should('exist')

    cy.visit('/new-batch')
    cy.get('@system-prompt').should('have.value', 'Bob\'s prompt.')
    cy.get('@input-text').eq(0).should('have.value', 'Bob\'s input.')
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Alice', {delay: 0})
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('@system-prompt').should('have.value', 'Alice\'s prompt.')
    cy.get('@input-text').eq(0).should('have.value', 'Alice\'s input.')
  })

  it('submits a batch and refreshes until it is ready', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Sleep 2', {delay: 0})

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('button:contains("View details")').should('be.disabled')
    cy.get('button:contains("View details")').should('be.enabled')
  })

  it('handles non-JSON response from the LLM', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Not JSON', {delay: 0})

    cy.get('button:contains("Submit")').click()

    cy.get('h2:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("Failed to parse JSON response")').should('exist')
  })

  it('handles invalid JSON response from the LLM', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Invalid JSON', {delay: 0})

    cy.get('button:contains("Submit")').click()

    cy.get('h2:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("Failed to validate JSON response")').should('exist')
  })
})


describe('The batch edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')

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

  it('displays "Not found" when the batch does not exist', () => {
    cy.visit('/batch-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('looks like this', () => {
    cy.visit('/batch-1')

    cy.compareSnapshot({name: `batch-edition-page.1.${Cypress.browser.name}`, cypressScreenshotOptions: {disableTimersAndAnimations: true}})

    cy.get('button:contains("Full screen")').eq(0).click()

    cy.compareSnapshot(`batch-edition-page.2.${Cypress.browser.name}`)
  })
})


describe('The adaptation edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)

    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')

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

  it('looks like this', () => {
    cy.visit('/adaptation-1')

    cy.get('h1:contains("Adapted exercise")').should('exist')
    cy.compareSnapshot(`adaptation-edition-page.${Cypress.browser.name}`)
  })

  it('displays "Not found" when the adaptation does not exist', () => {
    cy.visit('/adaptation-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('enables the "submit adjustment" button', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').as('user-prompt')
    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')

    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
    cy.get('@user-prompt').type('Blah.', {delay: 0})
    cy.get('@user-prompt').should('have.value', 'Blah.')
    cy.get('@submit-adjustment').should('be.enabled')
    cy.get('@user-prompt').type('{selectAll}{del}', {delay: 0})
    cy.get('@user-prompt').should('have.value', '')
    cy.get('@submit-adjustment').should('be.disabled')
  })

  it('submits and rewinds adjustments', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').as('user-prompt')
    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')

    cy.get('@user-prompt').type('Blah.', {delay: 0})
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist')
    cy.get('@user-prompt').type('Bleh.', {delay: 0})
    cy.get('@submit-adjustment').click()
    cy.get('@user-prompt').should('have.value', '')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('not.exist')
    cy.get('div.user-prompt:contains("Bleh.")').should('exist')
    cy.get('div.user-prompt:contains("Bleh.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Bleh.")').should('not.exist')
    cy.get('div.user-prompt:contains("Blah.")').should('exist')
    cy.get('div.user-prompt:contains("Blah.")').find('div:contains("❌")').should('exist').click()
    cy.get('div.user-prompt:contains("Blah.")').should('not.exist')
  })

  const unformattedJson = '{"format":"v1","instruction":{"lines":[{"contents":[{"kind":"text","text":"Blah"}]}]},"example":null,"hint":null,"statement":{"pages":[]},"reference":null}'
  const formattedJson = '{\n  "format": "v1",\n  "instruction": {"lines": [{"contents": [{"kind": "text", "text": "Blah"}]}]},\n  "example": null,\n  "hint": null,\n  "statement": {"pages": []},\n  "reference": null\n}'

  it('reformats manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@manual-edition').type('{selectAll}').type(unformattedJson, {delay: 0, parseSpecialCharSequences: false})
    cy.get('@manual-edition').should('have.value', unformattedJson)
    cy.get('button[data-cy="reformat-manual-edition"]').click()
    cy.get('@manual-edition').should('have.value', formattedJson)
  })

  it('saves manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@manual-edition').type('{selectAll}').type(unformattedJson, {delay: 0, parseSpecialCharSequences: false})

    cy.visit('/adaptation-1')

    cy.get('@manual-edition').should('have.value', formattedJson)
  })

  it('forbids adjustments on manual edits', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="submit-adjustment"]').as('submit-adjustment')
    cy.get('[data-cy="manual-edition"]').as('manual-edition')

    cy.get('@submit-adjustment').should('exist')
    cy.get('@manual-edition').type('Blih blih.', {delay: 0})
    cy.get('@submit-adjustment').should('not.exist')
    cy.get('[data-cy="reset-manual-edition"]').click()
    cy.get('@submit-adjustment').should('exist')
  })

  it('handles non-JSON response from the LLM and rewinds it', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').type('{selectAll}Not JSON', {delay: 0})

    cy.get('[data-cy="submit-adjustment"]').click()

    cy.get('h1:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("Failed to parse JSON response")').should('exist')
    cy.get('h1:contains("Adapted exercise")').should('not.exist')

    cy.get('div:contains("❌")').last().click()

    cy.get('h1:contains("Error with the LLM")').should('not.exist')
    cy.get('h1:contains("Adapted exercise")').should('exist')
  })

  it('handles invalid JSON response from the LLM', () => {
    cy.visit('/adaptation-1')

    cy.get('[data-cy="user-prompt"]').type('{selectAll}Invalid JSON', {delay: 0})

    cy.get('[data-cy="submit-adjustment"]').click()

    cy.get('h1:contains("Error with the LLM")').should('exist')
    cy.get('p:contains("Failed to validate JSON response")').should('exist')
    cy.get('h1:contains("Adapted exercise")').should('not.exist')

    cy.get('div:contains("❌")').last().click()

    cy.get('h1:contains("Error with the LLM")').should('not.exist')
    cy.get('h1:contains("Adapted exercise")').should('exist')
  })
})
