function ignoreResizeObserverLoopError() {
  Cypress.on('uncaught:exception', (error) => {
    if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
      // @todo Deep dive into this issue: avoid the error instead of ignoring it.
      // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
      return false
    } else {
      return true
    }
  })
}

function screenshot(name: string) {
  cy.compareSnapshot({
    name: `${name}.${Cypress.browser.name}`,
    cypressScreenshotOptions: { disableTimersAndAnimations: true },
  })
}

describe('The batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')
    ignoreResizeObserverLoopError()
    cy.visit('/new-batch')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('looks like this', () => {
    screenshot('batch-creation-page')
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

    cy.visit('/new-batch')
    cy.get('@llm-name').should('have.value', 'dummy-2')
  })

  it('remembers the last system prompt used', () => {
    cy.get('[data-cy="system-prompt"]').as('system-prompt')

    cy.get('@system-prompt').type(' Blih blih.', { delay: 0 })
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
    cy.get('@input-text').eq(0).type('{selectAll}Blah blah.', { delay: 0 })
    cy.get('@input-text').eq(1).type('{selectAll}Bleh bleh.', { delay: 0 })
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

    cy.visit('/new-batch')
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

    cy.visit('/new-batch')
    cy.get('@system-prompt').should('have.value', "Bob's prompt.")
    cy.get('@input-text').eq(0).should('have.value', "Bob's input.")
    cy.get('[data-cy="edit-identified-user"]').click()
    cy.get('[data-cy="identified-user"]').type('{selectAll}Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
    cy.get('@system-prompt').should('have.value', "Alice's prompt.")
    cy.get('@input-text').eq(0).should('have.value', "Alice's input.")
  })

  it('submits a batch and refreshes until it is ready', () => {
    cy.get('[data-cy="input-text"]').eq(0).type('{selectAll}Sleep 2', { delay: 0 })

    cy.get('button:contains("Submit")').click()
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('button:contains("View details")').should('be.disabled')
    cy.get('button:contains("View details")').should('be.enabled')
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
})

describe('The batch edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
    ignoreResizeObserverLoopError()
  })

  it('displays "Not found" when the batch does not exist', () => {
    cy.visit('/batch-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('displays "Not found" when the batch id is not an integer', () => {
    cy.visit('/batch-nope')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('looks like this', () => {
    cy.visit('/batch-1')

    screenshot('batch-edition-page.1')

    cy.get('button:contains("Full screen")').eq(0).click()

    screenshot('batch-edition-page.2')
  })

  it('does not remember answers', () => {
    cy.visit('/batch-1')

    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    cy.get('[data-cy="choice0"]').click()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('contain', 'vent')

    cy.visit('/batch-1')
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).should('not.contain', 'vent')
  })
})

describe('The adaptation edition page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
    ignoreResizeObserverLoopError()
  })

  it('displays "Not found" when the adaptation does not exist', () => {
    cy.visit('/adaptation-42')

    cy.get('h1:contains("Not found")').should('exist')
  })

  it('displays "Not found" when the adaptation id is not an integer', () => {
    cy.visit('/adaptation-nope')

    cy.get('h1:contains("Not found")').should('exist')
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
    .type('{selectAll}')
    .type(validExercise.unformattedJson, { delay: 0, parseSpecialCharSequences: false })
}

function invalidateJsonManually() {
  cy.get('@manual-edition').type('{selectAll}').type('{}', { delay: 0, parseSpecialCharSequences: false })
}

function breakJsonManually() {
  cy.get('@manual-edition').type('{selectAll}Not JSON.', { delay: 0 })
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
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
    ignoreResizeObserverLoopError()
    cy.visit('/adaptation-1')
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

  it('invalidate the JSON manually', () => {
    invalidateJsonManually()
    shouldBeManualInvalidJson()
    screenshot('adaptation-edition-page.manual-invalid')
  })

  it('breaks the JSON manually', () => {
    breakJsonManually()
    shouldBeManualNotJson()
    screenshot('adaptation-edition-page.manual-not-json')
  })
})

describe('The edition page for an initially invalid-json adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
    ignoreResizeObserverLoopError()
    cy.visit('/adaptation-3')
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

  it('invalidate the JSON manually', () => {
    invalidateJsonManually()
    shouldBeManualInvalidJson()
  })

  it('breaks the JSON manually', () => {
    breakJsonManually()
    shouldBeManualNotJson()
  })
})

describe('The edition page for an initially not-json adaptation', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=mixed-dummy-batch')
    ignoreResizeObserverLoopError()
    cy.visit('/adaptation-4')
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
})
