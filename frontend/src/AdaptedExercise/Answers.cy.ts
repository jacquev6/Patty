import type { AdaptedExercise } from '@/apiClient'
import AdaptedExerciseRenderer, { type StudentAnswers } from './AdaptedExerciseRenderer.vue'

describe('Adapted exercise answers', () => {
  const studentAnswersStorageKey = '1'
  const answersKey = `patty/student-answers/v2/exercise-${studentAnswersStorageKey}`

  const emptyAnswers: StudentAnswers = {
    pages: {},
  }

  const exerciseWithFreeTextInputs: AdaptedExercise = {
    format: 'v1',
    instruction: { lines: [] },
    example: null,
    hint: null,
    statement: {
      pages: [
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
          ],
        },
        {
          lines: [
            {
              contents: [
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'freeTextInput' },
              ],
            },
          ],
        },
      ],
    },
    reference: null,
  }

  const answersForFreeTextInputs: StudentAnswers = {
    pages: {
      '0': {
        lines: {
          '0': { components: { '2': { kind: 'freeTextInput', text: '0' }, '6': { kind: 'freeTextInput', text: '1' } } },
          '1': {
            components: {
              '0': { kind: 'freeTextInput', text: '2' },
              '4': { kind: 'freeTextInput', text: '3' },
              '8': { kind: 'freeTextInput', text: '4' },
            },
          },
          '2': { components: { '2': { kind: 'freeTextInput', text: '5' }, '6': { kind: 'freeTextInput', text: '6' } } },
        },
      },
      '1': {
        lines: {
          '0': {
            components: { '0': { kind: 'freeTextInput', text: '7' }, '8': { kind: 'freeTextInput', text: '9' } },
          },
          '1': {
            components: { '6': { kind: 'freeTextInput', text: '11' } },
          },
          '2': {
            components: { '4': { kind: 'freeTextInput', text: '13' } },
          },
        },
      },
    },
  }

  const colors = ['rgb(128, 0, 0)', 'rgb(0, 128, 0)', 'rgb(0, 0, 128)', 'rgba(0, 0, 0, 0)']

  const exerciseWithSelectableInputs: AdaptedExercise = {
    format: 'v1',
    instruction: { lines: [] },
    example: null,
    hint: null,
    statement: {
      pages: [
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'a' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'b' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'c' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'd' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'e' }], colors, boxed: false },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'f' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'g' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
          ],
        },
        {
          lines: [
            {
              contents: [
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'h' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'i' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'j' }], colors, boxed: false },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'k' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'l' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'm' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'n' }], colors, boxed: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'selectableInput', contents: [{ kind: 'text', text: 'o' }], colors, boxed: false },
              ],
            },
          ],
        },
      ],
    },
    reference: null,
  }

  const answersForSelectableInputs: StudentAnswers = {
    pages: {
      '0': {
        lines: {
          '0': {
            components: {
              '2': { kind: 'selectableInput', color: 1 },
              '6': { kind: 'selectableInput', color: 2 },
            },
          },
          '1': {
            components: {
              '0': { kind: 'selectableInput', color: 3 },
              '4': { kind: 'selectableInput', color: 4 },
              '8': { kind: 'selectableInput', color: 1 },
            },
          },
          '2': {
            components: {
              '2': { kind: 'selectableInput', color: 2 },
              '6': { kind: 'selectableInput', color: 3 },
            },
          },
        },
      },
      '1': {
        lines: {
          '0': {
            components: {
              '0': { kind: 'selectableInput', color: 1 },
              '8': { kind: 'selectableInput', color: 3 },
            },
          },
          '1': {
            components: {
              '6': { kind: 'selectableInput', color: 2 },
            },
          },
          '2': {
            components: {
              '4': { kind: 'selectableInput', color: 1 },
            },
          },
        },
      },
    },
  }

  const choices = [
    { contents: [{ kind: 'text' as const, text: '0' }] },
    { contents: [{ kind: 'text' as const, text: '1' }] },
    { contents: [{ kind: 'text' as const, text: '2' }] },
  ]

  const exerciseWithMultipleChoicesInputs: AdaptedExercise = {
    format: 'v1',
    instruction: { lines: [] },
    example: null,
    hint: null,
    statement: {
      pages: [
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
          ],
        },
        {
          lines: [
            {
              contents: [
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
              ],
            },
          ],
        },
      ],
    },
    reference: null,
  }

  const answersForMultipleChoicesInputs: StudentAnswers = {
    pages: {
      '0': {
        lines: {
          '0': {
            components: {
              '2': { kind: 'multipleChoicesInput', choice: 0 },
              '6': { kind: 'multipleChoicesInput', choice: 1 },
            },
          },
          '1': {
            components: {
              '0': { kind: 'multipleChoicesInput', choice: 2 },
              '4': { kind: 'multipleChoicesInput', choice: 0 },
              '8': { kind: 'multipleChoicesInput', choice: 1 },
            },
          },
          '2': {
            components: {
              '2': { kind: 'multipleChoicesInput', choice: 2 },
              '6': { kind: 'multipleChoicesInput', choice: 0 },
            },
          },
        },
      },
      '1': {
        lines: {
          '0': {
            components: {
              '0': { kind: 'multipleChoicesInput', choice: 0 },
              '8': { kind: 'multipleChoicesInput', choice: 2 },
            },
          },
          '1': {
            components: {
              '6': { kind: 'multipleChoicesInput', choice: 1 },
            },
          },
          '2': {
            components: {
              '4': { kind: 'multipleChoicesInput', choice: 0 },
            },
          },
        },
      },
    },
  }

  const exerciseWithSwappableInputs: AdaptedExercise = {
    format: 'v1',
    instruction: { lines: [] },
    example: null,
    hint: null,
    statement: {
      pages: [
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'a' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'b' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
            {
              contents: [
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'c' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'd' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'e' }] },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'f' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                { kind: 'swappableInput', contents: [{ kind: 'text', text: 'g' }] },
                { kind: 'whitespace' },
                { kind: 'text', text: 'C' },
              ],
            },
          ],
        },
      ],
    },
    reference: null,
  }

  const answersForSwappableInputs: StudentAnswers = {
    pages: {
      '0': {
        lines: {
          '0': {
            components: {
              '2': { kind: 'swappableInput', contentsFrom: { pageIndex: 0, lineIndex: 1, componentIndex: 4 } },
            },
          },
          '1': {
            components: {
              '4': { kind: 'swappableInput', contentsFrom: { pageIndex: 0, lineIndex: 2, componentIndex: 6 } },
            },
          },
          '2': {
            components: {
              '2': { kind: 'swappableInput', contentsFrom: { pageIndex: 0, lineIndex: 0, componentIndex: 2 } },
              '6': { kind: 'swappableInput', contentsFrom: { pageIndex: 0, lineIndex: 2, componentIndex: 2 } },
            },
          },
        },
      },
    },
  }

  function getAnswers(): Cypress.Chainable<StudentAnswers> {
    return cy.getAllLocalStorage().then(Object.values).its(0).its(answersKey).then(JSON.parse)
  }

  function setAnswers(answers: StudentAnswers) {
    localStorage.setItem(answersKey, JSON.stringify(answers))
  }

  it('are saved for free text inputs', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithFreeTextInputs,
      },
    })

    getAnswers().should('deep.equal', emptyAnswers)

    for (let i = 0; i < 7; i++) {
      cy.get('[data-cy="freeTextInput"]')
        .eq(i)
        .should('have.text', '')
        .type(i.toString(), { delay: 0 })
        .should('have.text', i.toString())
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      cy.get('[data-cy="freeTextInput"]')
        .eq(i)
        .should('have.text', '')
        .type((i + 7).toString(), { delay: 0 })
        .should('have.text', (i + 7).toString())
    }

    getAnswers().should('deep.equal', answersForFreeTextInputs)
  })

  it('are loaded for free text inputs', () => {
    setAnswers(answersForFreeTextInputs)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithFreeTextInputs,
      },
    })

    for (let i = 0; i < 7; i++) {
      cy.get('[data-cy="freeTextInput"]').eq(i).should('have.text', i.toString())
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      cy.get('[data-cy="freeTextInput"]')
        .eq(i)
        .should('have.text', (i + 7).toString())
    }
    for (let i = 1; i < 8; i += 2) {
      cy.get('[data-cy="freeTextInput"]').eq(i).should('have.text', '')
    }
  })

  it('are saved for selectable inputs', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithSelectableInputs,
      },
    })

    getAnswers().should('deep.equal', emptyAnswers)

    for (let i = 0; i < 7; i++) {
      for (let k = 0; k <= i % 4; k++) {
        cy.get('[data-cy="selectableInput"]').eq(i).click()
      }
      cy.get('[data-cy="selectableInput"]')
        .eq(i)
        .should('have.css', 'background-color', colors[i % 4])
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      for (let k = 0; k <= i % 3; k++) {
        cy.get('[data-cy="selectableInput"]').eq(i).click()
      }
      cy.get('[data-cy="selectableInput"]')
        .eq(i)
        .should('have.css', 'background-color', colors[i % 3])
    }

    getAnswers().should('deep.equal', answersForSelectableInputs)
  })

  it('are loaded for selectable inputs', () => {
    setAnswers(answersForSelectableInputs)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithSelectableInputs,
      },
    })

    for (let i = 0; i < 7; i++) {
      cy.get('[data-cy="selectableInput"]')
        .eq(i)
        .should('have.css', 'background-color', colors[i % 4])
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      cy.get('[data-cy="selectableInput"]')
        .eq(i)
        .should('have.css', 'background-color', colors[i % 3])
    }
    for (let i = 1; i < 8; i += 2) {
      cy.get('[data-cy="selectableInput"]').eq(i).should('have.css', 'background-color', colors[3])
    }
  })

  it('are saved for multiple choices inputs', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithMultipleChoicesInputs,
      },
    })

    getAnswers().should('deep.equal', emptyAnswers)

    for (let i = 0; i < 7; i++) {
      cy.get('[data-cy="multipleChoicesInput"]').eq(i).click()
      cy.get(`[data-cy="choice${i % 3}"]`).click()
      cy.get('[data-cy="multipleChoicesInput"]')
        .eq(i)
        .should('have.text', (i % 3).toString())
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      cy.get('[data-cy="multipleChoicesInput"]').eq(i).click()
      cy.get(`[data-cy="choice${i % 3}"]`).click()
      cy.get('[data-cy="multipleChoicesInput"]')
        .eq(i)
        .should('have.text', (i % 3).toString())
    }

    getAnswers().should('deep.equal', answersForMultipleChoicesInputs)
  })

  it('are loaded for multiple choices inputs', () => {
    setAnswers(answersForMultipleChoicesInputs)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithMultipleChoicesInputs,
      },
    })

    for (let i = 0; i < 7; i++) {
      cy.get('[data-cy="multipleChoicesInput"]')
        .eq(i)
        .should('have.text', (i % 3).toString())
    }
    cy.get('.control').eq(1).click()
    for (let i = 0; i < 8; i += 2) {
      cy.get('[data-cy="multipleChoicesInput"]')
        .eq(i)
        .should('have.text', (i % 3).toString())
    }
    for (let i = 1; i < 8; i += 2) {
      cy.get('[data-cy="multipleChoicesInput"]').eq(i).should('have.text', '....')
    }
  })

  it('are saved for swappable inputs', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithSwappableInputs,
      },
    })

    getAnswers().should('deep.equal', emptyAnswers)

    cy.get('[data-cy="swappableInput"]').eq(0).click()
    cy.get('[data-cy="swappableInput"]').eq(3).click()
    cy.get('[data-cy="swappableInput"]').eq(3).click()
    cy.get('[data-cy="swappableInput"]').eq(5).click()
    cy.get('[data-cy="swappableInput"]').eq(6).click()
    cy.get('[data-cy="swappableInput"]').eq(3).click()

    cy.get('[data-cy="swappableInput"]').eq(0).should('have.text', 'd')
    cy.get('[data-cy="swappableInput"]').eq(1).should('have.text', 'b')
    cy.get('[data-cy="swappableInput"]').eq(2).should('have.text', 'c')
    cy.get('[data-cy="swappableInput"]').eq(3).should('have.text', 'g')
    cy.get('[data-cy="swappableInput"]').eq(4).should('have.text', 'e')
    cy.get('[data-cy="swappableInput"]').eq(5).should('have.text', 'a')
    cy.get('[data-cy="swappableInput"]').eq(6).should('have.text', 'f')

    getAnswers().should('deep.equal', answersForSwappableInputs)
  })

  it('are loaded for swappable inputs', () => {
    setAnswers(answersForSwappableInputs)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithSwappableInputs,
      },
    })

    cy.get('[data-cy="swappableInput"]').eq(0).should('have.text', 'd')
    cy.get('[data-cy="swappableInput"]').eq(1).should('have.text', 'b')
    cy.get('[data-cy="swappableInput"]').eq(2).should('have.text', 'c')
    cy.get('[data-cy="swappableInput"]').eq(3).should('have.text', 'g')
    cy.get('[data-cy="swappableInput"]').eq(4).should('have.text', 'e')
    cy.get('[data-cy="swappableInput"]').eq(5).should('have.text', 'a')
    cy.get('[data-cy="swappableInput"]').eq(6).should('have.text', 'f')
  })

  const exerciseWithEditableTextInputs: AdaptedExercise = {
    format: 'v1',
    instruction: { lines: [] },
    example: null,
    hint: null,
    statement: {
      pages: [
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'A' },
                { kind: 'whitespace' },
                {
                  kind: 'editableTextInput',
                  contents: [{ kind: 'text', text: 'a0' }, { kind: 'whitespace' }, { kind: 'text', text: 'a1' }],
                },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'B' },
                { kind: 'whitespace' },
                {
                  kind: 'editableTextInput',
                  contents: [
                    { kind: 'text', text: 'b0' },
                    { kind: 'whitespace' },
                    { kind: 'text', text: 'b1' },
                    { kind: 'whitespace' },
                    { kind: 'text', text: 'b2' },
                  ],
                },
              ],
            },
          ],
        },
        {
          lines: [
            {
              contents: [
                { kind: 'text', text: 'C' },
                { kind: 'whitespace' },
                {
                  kind: 'editableTextInput',
                  contents: [{ kind: 'text', text: 'c0' }, { kind: 'whitespace' }, { kind: 'text', text: 'c1' }],
                },
              ],
            },
            {
              contents: [
                { kind: 'text', text: 'D' },
                { kind: 'whitespace' },
                {
                  kind: 'editableTextInput',
                  contents: [{ kind: 'text', text: 'd0' }, { kind: 'whitespace' }, { kind: 'text', text: 'd1' }],
                },
              ],
            },
          ],
        },
      ],
    },
    reference: null,
  }

  const answersForEditableTextInputs: StudentAnswers = {
    pages: {
      '0': {
        lines: {
          '0': {
            components: {
              '2': { kind: 'editableTextInput', text: 'AAA AAA' },
            },
          },
          '1': {
            components: {
              '2': { kind: 'editableTextInput', text: 'BBB BBB' },
            },
          },
        },
      },
      '1': {
        lines: {
          '0': {
            components: {
              '2': { kind: 'editableTextInput', text: 'CCC CCC' },
            },
          },
        },
      },
    },
  }

  it('are saved for editable text inputs', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithEditableTextInputs,
      },
    })

    getAnswers().should('deep.equal', emptyAnswers)

    cy.get('[data-cy="freeTextInput"]').eq(0).should('have.text', 'a0 a1').type('{selectAll}AAA AAA', { delay: 0 })
    cy.get('[data-cy="freeTextInput"]').eq(1).should('have.text', 'b0 b1 b2').type('{selectAll}BBB BBB', { delay: 0 })
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').eq(0).should('have.text', 'c0 c1').type('{selectAll}CCC CCC', { delay: 0 })
    cy.get('[data-cy="freeTextInput"]').eq(1).should('have.text', 'd0 d1')

    getAnswers().should('deep.equal', answersForEditableTextInputs)
  })

  it('are loaded for editable text inputs', () => {
    setAnswers(answersForEditableTextInputs)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey,
        adaptedExercise: exerciseWithEditableTextInputs,
      },
    })

    cy.get('[data-cy="freeTextInput"]').eq(0).should('have.text', 'AAA AAA')
    cy.get('[data-cy="freeTextInput"]').eq(1).should('have.text', 'BBB BBB')
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').eq(0).should('have.text', 'CCC CCC')
    cy.get('[data-cy="freeTextInput"]').eq(1).should('have.text', 'd0 d1')
  })
})
