// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import { createI18n } from 'vue-i18n'

import AdaptedExerciseRenderer from './AdaptedExerciseRenderer.vue'
import TriColorLines from './TriColorLines.vue'
import assert from '$/assert'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  if (!Cypress.config('isInteractive')) {
    const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
    screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
    const name = `${baseName}-${screenshotsCounts[baseName]}`
    cy.compareSnapshot(name)
  }
}

const global = { plugins: [createI18n({ legacy: false, locale: 'fr' })] }

describe('FormattedComponent', () => {
  it('renders plain text and whitespace', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Some' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'casual' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('p').should('have.text', 'Some casual text.')
    screenshot()
  })

  it('renders bold', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Bold' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                    bold: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders italic', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Italic' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                    italic: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders underlined', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Underlined' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                    underlined: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders highlighted', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Highlighted' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                    highlighted: 'yellow',
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders boxed', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'Boxed' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'text' },
                      { kind: 'text', text: '.' },
                    ],
                    boxed: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders complex nested formatting', () => {
    cy.viewport(700, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'formatted',
                    contents: [
                      { kind: 'text', text: 'bold' },
                      { kind: 'whitespace' },
                      {
                        kind: 'formatted',
                        contents: [
                          { kind: 'text', text: 'boxed' },
                          { kind: 'whitespace' },
                          {
                            kind: 'formatted',
                            contents: [{ kind: 'text', text: 'italic' }],
                            italic: true,
                          },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'boxed' },
                        ],
                        boxed: true,
                      },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'bold' },
                    ],
                    bold: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders superscript', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'Base' },
                  {
                    kind: 'formatted',
                    contents: [{ kind: 'text', text: 'super' }],
                    superscript: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })

  it('renders subscript', () => {
    cy.viewport(500, 260)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'Base' },
                  {
                    kind: 'formatted',
                    contents: [{ kind: 'text', text: 'sub' }],
                    subscript: true,
                  },
                ],
              },
            ],
          },
          example: null,
          hint: null,
          statement: { pages: [] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })
})

describe('SelectableInput', () => {
  it('changes color on click', () => {
    cy.viewport(500, 310)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Click' },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'us' },
                          { kind: 'text', text: '!' },
                        ],
                        colors: ['rgb(255, 0, 0)', 'rgb(0, 128, 0)'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').should('have.length', 1)
    cy.get('@input').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')
    cy.get('@input').click()
    screenshot()
    cy.get('@input').should('have.css', 'background-color', 'rgb(255, 0, 0)')
    cy.get('@input').click()
    screenshot()
    cy.get('@input').should('have.css', 'background-color', 'rgb(0, 128, 0)')
    cy.get('@input').click()
    screenshot()
    cy.get('@input').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')
  })

  it('adds padding to single letters and punctuation', () => {
    cy.viewport(500, 310)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'Word' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').click()
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'Word' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click({ multiple: true })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'X' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click({ multiple: true })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: '.' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: '.' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Jusqu' },
                          { kind: 'text', text: "'" },
                        ],
                        colors: ['grey'],
                        boxed: false,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'à' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                      { kind: 'whitespace' },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'point' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: '.' }],
                        colors: ['grey'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click({ multiple: true })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Jusqu' },
                          { kind: 'text', text: "'" },
                        ],
                        colors: ['grey'],
                        boxed: true,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'à' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                      { kind: 'whitespace' },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: 'point' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                      {
                        kind: 'selectableInput',
                        contents: [{ kind: 'text', text: '.' }],
                        colors: ['grey'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('@input').click({ multiple: true })
    screenshot()
  })

  it('renders nested selectable inputs', () => {
    cy.viewport(550, 310)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Ext' },
                          { kind: 'whitespace' },
                          {
                            kind: 'selectableInput',
                            contents: [{ kind: 'text', text: 'in' }],
                            colors: ['red'],
                            boxed: false,
                          },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'ext' },
                          { kind: 'text', text: '.' },
                        ],
                        colors: ['yellow'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').click('left', { multiple: true })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Ext' },
                          { kind: 'whitespace' },
                          {
                            kind: 'selectableInput',
                            contents: [
                              { kind: 'text', text: 'mid' },
                              { kind: 'whitespace' },
                              {
                                kind: 'selectableInput',
                                contents: [{ kind: 'text', text: 'inner' }],
                                colors: ['orange'],
                                boxed: false,
                              },
                              { kind: 'whitespace' },
                              { kind: 'text', text: 'mid' },
                            ],
                            colors: ['grey'],
                            boxed: false,
                          },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'ext' },
                          { kind: 'text', text: '.' },
                        ],
                        colors: ['yellow'],
                        boxed: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').click('left', { multiple: true })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'selectableInput',
                        contents: [
                          { kind: 'text', text: 'Ext' },
                          { kind: 'whitespace' },
                          {
                            kind: 'selectableInput',
                            contents: [
                              { kind: 'text', text: 'mid' },
                              { kind: 'whitespace' },
                              {
                                kind: 'selectableInput',
                                contents: [{ kind: 'text', text: 'inner' }],
                                colors: ['orange'],
                                boxed: true,
                              },
                              { kind: 'whitespace' },
                              { kind: 'text', text: 'mid' },
                            ],
                            colors: ['grey'],
                            boxed: true,
                          },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'ext' },
                          { kind: 'text', text: '.' },
                        ],
                        colors: ['yellow'],
                        boxed: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').click('left', { multiple: true })
    screenshot()
  })
})

describe('FreeTextInput', () => {
  it('accepts text input', () => {
    cy.viewport(500, 310)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: { lines: [] },
          example: null,
          hint: null,
          statement: { pages: [{ lines: [{ contents: [{ kind: 'freeTextInput' }] }] }] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').should('have.length', 1)
    cy.get('@input').click() // The input has non-zero width and height
    screenshot()
    cy.get('@input').type('Hello,')
    screenshot()
    cy.get('@input').type(' world!')
    screenshot()
    cy.get('@input').should('have.text', 'Hello, world!')
  })

  it('handles new lines', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: { lines: [] },
          example: null,
          hint: null,
          statement: { pages: [{ lines: [{ contents: [{ kind: 'freeTextInput' }] }] }] },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').type('Hello{enter}world')
    cy.get('br').should('not.exist')
    if (Cypress.browser.name === 'firefox') {
      cy.get('@input').should('have.text', 'Hello\nworld')
    } else {
      cy.get('@input').should('have.text', 'Hello\nworld\n')
    }
  })

  it('handles arrow keys normally, blurs on Escape to navigate pages', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'text', text: 'Page' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: '1' },
                      { kind: 'whitespace' },
                      { kind: 'freeTextInput' },
                    ],
                  },
                ],
              },
              {
                lines: [
                  {
                    contents: [
                      { kind: 'text', text: 'Page' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: '2' },
                      { kind: 'whitespace' },
                      { kind: 'freeTextInput' },
                    ],
                  },
                ],
              },
              {
                lines: [
                  {
                    contents: [
                      { kind: 'text', text: 'Page' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: '3' },
                      { kind: 'whitespace' },
                      { kind: 'freeTextInput' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    // In Cypress, we have to trigger the two events
    function pressAndRelease(key: string) {
      cy.document().trigger('keydown', { key })
      cy.wait(0)
      cy.document().trigger('keyup', { key })
    }

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('p').should('contain.text', 'Page 1')
    cy.get('@input').type('One')
    cy.get('p').should('have.text', 'Page 1 One')
    cy.get('@input').type('{leftArrow}{leftArrow}TWO')
    cy.get('p').should('have.text', 'Page 1 OTWOne')
    cy.document().trigger('keydown', { key: 'Escape' })
    cy.document().trigger('keyup', { key: 'Escape' })
    cy.get('p').should('contain.text', 'Page 1')
    pressAndRelease('ArrowRight')
    cy.get('p').should('contain.text', 'Page 2')
    pressAndRelease('ArrowRight')
    cy.get('p').should('contain.text', 'Page 3')
    pressAndRelease('ArrowRight')
    cy.get('p').should('contain.text', "Quitter l'exercice")
    pressAndRelease('ArrowRight')
    cy.get('p').should('contain.text', "Quitter l'exercice")
    pressAndRelease('ArrowLeft')
    cy.get('p').should('contain.text', 'Page 3')
    pressAndRelease('ArrowLeft')
    cy.get('p').should('contain.text', 'Page 2')
    pressAndRelease('ArrowLeft')
    cy.get('p').should('contain.text', 'Page 1')
    pressAndRelease('ArrowLeft')
    cy.get('p').should('contain.text', 'Page 1')
  })

  function inputShouldHaveValue(v: string) {
    cy.getAllLocalStorage()
      .then(Object.values)
      .its(0)
      .its('patty/student-answers/v3/exercise-answers')
      .then(JSON.parse)
      .its('stmt-pg0-ln0-ct3.text')
      .should('equal', v)
    cy.get('@input').should('have.text', v)
  }

  it('spans several lines', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey: 'answers',
        adaptedExercise: {
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
                      { kind: 'text', text: 'a' },
                      { kind: 'text', text: '.' },
                      { kind: 'whitespace' },
                      { kind: 'freeTextInput' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').type('{selectAll}Hello, this is a long free text that spans several lines.')
    screenshot()
    inputShouldHaveValue('Hello, this is a long free text that spans several lines.')
  })

  it('supports standard edition', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey: 'answers',
        adaptedExercise: {
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
                      { kind: 'text', text: 'a' },
                      { kind: 'text', text: '.' },
                      { kind: 'whitespace' },
                      { kind: 'freeTextInput' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="freeTextInput"]').as('input')

    function reset(start: number, end: number) {
      cy.get('@input').type('{selectAll}Word1 word2 word3.', { delay: 0 })
      inputShouldHaveValue('Word1 word2 word3.')
      cy.get('@input')
        .find('span')
        .eq(1)
        .then((el) => {
          const sel = window.getSelection()
          assert(sel !== null)
          sel.removeAllRanges()
          const range = document.createRange()
          range.setStart(el[0].childNodes[0], start)
          range.setEnd(el[0].childNodes[0], end)
          sel.addRange(range)
        })
      return cy.get('@input')
    }

    // Del (then type)
    reset(0, 0).type('{del}')
    inputShouldHaveValue('Word1 ord2 word3.')
    reset(0, 0).type('{del}{del}')
    inputShouldHaveValue('Word1 rd2 word3.')
    reset(0, 0).type('{del}{del}{del}WOR')
    inputShouldHaveValue('Word1 WORd2 word3.')
    reset(1, 1).type('{del}')
    inputShouldHaveValue('Word1 wrd2 word3.')
    reset(1, 1).type('{del}{del}')
    inputShouldHaveValue('Word1 wd2 word3.')
    reset(1, 1).type('{del}{del}{del}ORD')
    inputShouldHaveValue('Word1 wORD2 word3.')
    reset(5, 5).type('{del}')
    inputShouldHaveValue('Word1 word2word3.')
    reset(5, 5).type('{del}{del}')
    inputShouldHaveValue('Word1 word2ord3.')
    reset(5, 5).type('{del}{del}{del} WO')
    inputShouldHaveValue('Word1 word2 WOrd3.')
    // Backspace (then type)
    reset(0, 0).type('{backspace}')
    inputShouldHaveValue('Word1word2 word3.')
    reset(0, 0).type('{backspace}{backspace}')
    inputShouldHaveValue('Wordword2 word3.')
    reset(0, 0).type('{backspace}{backspace}{backspace}DI ')
    inputShouldHaveValue('WorDI word2 word3.')
    reset(4, 4).type('{backspace}')
    inputShouldHaveValue('Word1 wor2 word3.')
    reset(4, 4).type('{backspace}{backspace}')
    inputShouldHaveValue('Word1 wo2 word3.')
    reset(4, 4).type('{backspace}{backspace}{backspace}ORD')
    inputShouldHaveValue('Word1 wORD2 word3.')
    reset(5, 5).type('{backspace}')
    inputShouldHaveValue('Word1 word word3.')
    reset(5, 5).type('{backspace}{backspace}')
    inputShouldHaveValue('Word1 wor word3.')
    reset(5, 5).type('{backspace}{backspace}{backspace}RDT')
    inputShouldHaveValue('Word1 woRDT word3.')
    // Replace selection
    reset(0, 3).type('WOR')
    inputShouldHaveValue('Word1 WORd2 word3.')
    reset(1, 4).type('ORD')
    inputShouldHaveValue('Word1 wORD2 word3.')
    reset(2, 5).type('RDT')
    inputShouldHaveValue('Word1 woRDT word3.')
    // Delete selection then type
    reset(1, 4).type('{del}ORD')
    inputShouldHaveValue('Word1 wORD2 word3.')
    reset(1, 4).type('{backspace}ORD')
    inputShouldHaveValue('Word1 wORD2 word3.')
  })

  it('renders inside a formatted component', () => {
    cy.viewport(520, 170)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                        kind: 'formatted',
                        highlighted: 'pink',
                        contents: [
                          { kind: 'text', text: 'B' },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'C' },
                          { kind: 'whitespace' },
                          {
                            kind: 'formatted',
                            bold: true,
                            contents: [
                              { kind: 'text', text: 'D' },
                              { kind: 'whitespace' },
                              { kind: 'freeTextInput' },
                              { kind: 'whitespace' },
                              { kind: 'text', text: 'E' },
                            ],
                          },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'F' },
                        ],
                      },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'G' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').click()
    screenshot()
    cy.get('@input').type('Hello')
    screenshot()
    cy.get('@input').blur()
    screenshot()
  })
})

describe('MultipleChoicesInput', () => {
  const twoChoices = [
    {
      contents: [{ kind: 'text' as const, text: 'Alpha' }],
    },
    {
      contents: [{ kind: 'text' as const, text: 'Bravo' }],
    },
  ]

  const choices = [
    ...twoChoices,
    {
      contents: [{ kind: 'text' as const, text: 'Charlie' }],
    },
  ]

  it('selects choices', () => {
    cy.viewport(500, 500)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                        choices,
                        showChoicesByDefault: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('@input').should('have.length', 1)
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
    cy.get('@input').click()
    screenshot()
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="choice1"]').click()
    screenshot()
    cy.get('[data-cy="choice0"]').should('not.exist')
    cy.get('@input').should('have.text', 'Bravo')
    cy.get('@input').click()
    screenshot()
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="choice2"]').click()
    screenshot()
    cy.get('[data-cy="choice0"]').should('not.exist')
    cy.get('@input').should('have.text', 'Charlie')
  })

  it('closes choices on click on backdrop', () => {
    cy.viewport(700, 500)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                        choices,
                        showChoicesByDefault: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('[data-cy="choice0"]').should('not.exist')
    cy.get('@input').click()
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="backdrop"]').click()
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('closes choices on click on main span', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                        choices,
                        showChoicesByDefault: true,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="backdrop"]').should('not.exist')
    cy.get('@input').click()
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('closes choices when changing page', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                        choices,
                        showChoicesByDefault: false,
                      },
                    ],
                  },
                ],
              },
              {
                lines: [
                  {
                    contents: [
                      {
                        kind: 'multipleChoicesInput',
                        choices: twoChoices,
                        showChoicesByDefault: false,
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('@input').click()
    cy.get('[data-cy="choice0"]').should('exist')

    cy.get('div.control').eq(1).click()
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('moves next lines down', () => {
    cy.viewport(600, 800)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'text', text: 'Hello' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: true },
                      { kind: 'text', text: '!' },
                    ],
                  },
                  {
                    contents: [
                      { kind: 'text', text: 'Good' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'bye' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: true },
                      { kind: 'text', text: '!' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
  })

  it('does not move next lines down', () => {
    cy.viewport(600, 800)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'text', text: 'Hello' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false, reducedLineSpacing: true },
                      { kind: 'text', text: '!' },
                    ],
                  },
                  {
                    contents: [
                      { kind: 'text', text: 'Good' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'bye' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false },
                      { kind: 'text', text: '!' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="multipleChoicesInput"]').eq(0).click()
    screenshot()
  })

  it('does not render choices over the page navigation controls', () => {
    cy.viewport(543, 780)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                    contents: [{ kind: 'multipleChoicesInput', choices, showChoicesByDefault: true }],
                  },
                  {
                    contents: [
                      { kind: 'text', text: 'Blaaaaaaaaaaaaaaaaah' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: true },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
  })

  it('chooses the first two colors as complimentary to main color', () => {
    cy.viewport(500, 1000)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'text', text: 'Blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      {
                        kind: 'multipleChoicesInput',
                        choices: twoChoices,
                        showChoicesByDefault: true,
                      },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      {
                        kind: 'multipleChoicesInput',
                        choices: twoChoices,
                        showChoicesByDefault: true,
                      },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'whitespace' },
                      {
                        kind: 'multipleChoicesInput',
                        choices: twoChoices,
                        showChoicesByDefault: true,
                      },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'blah' },
                      { kind: 'text', text: '.' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })
    screenshot()
  })
})

describe('TriColorLines', () => {
  it('renders lines in alternating colors', () => {
    cy.viewport(180, 340)

    // Work around weird typing issue: props and slots seem incompatible; I don't want to prioritize investigation now.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    cy.mount(TriColorLines as any, {
      props: { tricolored: true },
      slots: {
        default:
          '<p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p>',
      },
    })

    screenshot()
  })

  it('renders lines in black', () => {
    cy.viewport(180, 340)

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    cy.mount(TriColorLines as any, {
      props: { tricolored: false },
      slots: {
        default:
          '<p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p>',
      },
    })

    screenshot()
  })

  it('warns about nested tricolorables', () => {
    cy.viewport(300, 110)

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    cy.mount(TriColorLines as any, {
      props: { tricolored: true },
      slots: {
        default: '<p><span class="tricolorable">B<span><span class="tricolorable">la</span></span>h</span></p>',
      },
    })

    screenshot()
  })

  it('renders in tricolored mode', () => {
    cy.viewport(500, 600)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey: 'answers',
        adaptedExercise: {
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
                      { kind: 'text', text: 'alpha' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'bravo' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'charlie' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'delta' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'echo' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'foxtrot' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'golf' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'hotel' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'india' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'juliet' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'kilo' },
                      { kind: 'whitespace' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
  })

  it('renders in black mode', () => {
    cy.viewport(500, 600)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        studentAnswersStorageKey: 'answers',
        adaptedExercise: {
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
                      { kind: 'text', text: 'alpha' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'bravo' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'charlie' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'delta' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'echo' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'foxtrot' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'golf' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'hotel' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'india' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'juliett' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'kilo' },
                      { kind: 'whitespace' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
        tricolored: false,
      },
      global,
    })

    screenshot()
  })
})

describe('SwappableInput', () => {
  it('renders', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'swappableInput',
                        contents: [
                          { kind: 'text', text: 'Swap' },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'me' },
                        ],
                      },
                    ],
                  },
                  {
                    contents: [
                      {
                        kind: 'swappableInput',
                        contents: [],
                      },
                      { kind: 'whitespace' },
                      {
                        kind: 'swappableInput',
                        contents: [{ kind: 'text', text: 'and' }, { kind: 'whitespace' }, { kind: 'text', text: 'me' }],
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="swappableInput"]').eq(0).click()
    cy.get('[data-cy="swappableInput"]').eq(0).should('have.css', 'background-color', 'rgb(255, 253, 212)')
    screenshot()
    cy.get('[data-cy="swappableInput"]').eq(0).click()
    cy.get('[data-cy="swappableInput"]').eq(0).should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')
  })

  it('swaps', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'A' }] },
                      { kind: 'whitespace' },
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'B' }] },
                    ],
                  },
                  {
                    contents: [
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'C' }] },
                      { kind: 'whitespace' },
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'D' }] },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="swappableInput"]').eq(0).as('a')
    cy.get('[data-cy="swappableInput"]').eq(1).as('b')
    cy.get('[data-cy="swappableInput"]').eq(2).as('c')
    cy.get('[data-cy="swappableInput"]').eq(3).as('d')

    cy.get('@a').should('have.text', 'A')
    cy.get('@b').should('have.text', 'B')
    cy.get('@c').should('have.text', 'C')
    cy.get('@d').should('have.text', 'D')

    cy.get('@a').click()
    cy.get('@b').click()
    cy.get('@a').should('have.text', 'B')
    cy.get('@b').should('have.text', 'A')
    cy.get('@c').should('have.text', 'C')
    cy.get('@d').should('have.text', 'D')

    cy.get('@a').click()
    cy.get('@b').click()
    cy.get('@a').should('have.text', 'A')
    cy.get('@b').should('have.text', 'B')
    cy.get('@c').should('have.text', 'C')
    cy.get('@d').should('have.text', 'D')

    cy.get('@c').click()
    cy.get('@b').click()
    cy.get('@a').should('have.text', 'A')
    cy.get('@b').should('have.text', 'C')
    cy.get('@c').should('have.text', 'B')
    cy.get('@d').should('have.text', 'D')

    cy.get('@a').click()
    cy.get('@d').click()
    cy.get('@a').should('have.text', 'D')
    cy.get('@b').should('have.text', 'C')
    cy.get('@c').should('have.text', 'B')
    cy.get('@d').should('have.text', 'A')
  })

  it('resets selected swappable when page is changed', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'A' }] },
                      { kind: 'whitespace' },
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'B' }] },
                    ],
                  },
                ],
              },
              {
                lines: [
                  {
                    contents: [
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'C' }] },
                      { kind: 'whitespace' },
                      { kind: 'swappableInput', contents: [{ kind: 'text', text: 'D' }] },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('[data-cy="swappableInput"]').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')
    cy.get('[data-cy="swappableInput"]').eq(0).click()
    cy.get('[data-cy="swappableInput"]').eq(0).should('have.css', 'background-color', 'rgb(255, 253, 212)')

    cy.get('.control').eq(1).click()
    cy.get('[data-cy="swappableInput"]').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')

    cy.get('.control').eq(0).click()
    cy.get('[data-cy="swappableInput"]').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)')
  })
})

describe('EditableTextInput', () => {
  it('renders', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      { kind: 'text', text: 'a' },
                      { kind: 'text', text: '.' },
                      { kind: 'whitespace' },
                      {
                        kind: 'editableTextInput',
                        showOriginalText: true,
                        contents: [
                          { kind: 'text', text: 'Edit' },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'me' },
                          { kind: 'text', text: '.' },
                        ],
                      },
                    ],
                  },
                  {
                    contents: [
                      { kind: 'text', text: 'm' },
                      { kind: 'text', text: '.' },
                      { kind: 'whitespace' },
                      {
                        kind: 'editableTextInput',
                        showOriginalText: true,
                        contents: [
                          { kind: 'text', text: 'And' },
                          { kind: 'whitespace' },
                          { kind: 'text', text: 'me' },
                          { kind: 'text', text: '.' },
                        ],
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
    cy.get('[data-cy="freeTextInput"]').eq(0).as('input')
    cy.get('@input').focus().type('{end}')
    screenshot()
    cy.get('@input').type('{backspace}eee.')
    screenshot()
  })
})

describe('SplitWordInput', () => {
  it('renders', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: { lines: [] },
          example: null,
          hint: null,
          statement: {
            pages: [
              {
                lines: [
                  {
                    contents: [{ kind: 'splitWordInput', word: 'Nolimber' }],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    // The '|' is better centered in an actual browser than on those screenshots. I can't figure out why...
    screenshot()
    cy.get('[data-cy="splitWordInput"]').eq(0).find('span.inter').eq(0).find('span').click()
    screenshot()
    cy.get('[data-cy="splitWordInput"]').eq(0).find('span.inter').eq(2).find('span').click()
    screenshot()
    cy.get('[data-cy="splitWordInput"]').eq(0).find('span.inter').eq(6).find('span').click()
    screenshot()
  })
})

describe('AdaptedExerciseRenderer', () => {
  it('supports exercise with zero pages in statement', () => {
    cy.viewport(600, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [{ contents: [{ kind: 'text', text: 'Hello' }] }],
          },
          example: null,
          hint: null,
          statement: {
            pages: [],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
  })

  it('renders the example and hint', () => {
    cy.viewport(600, 600)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [{ contents: [{ kind: 'text', text: 'Hello' }] }],
          },
          example: {
            lines: [{ contents: [{ kind: 'text', text: 'Example' }] }],
          },
          hint: {
            lines: [{ contents: [{ kind: 'text', text: 'Hint' }] }],
          },
          statement: {
            pages: [
              {
                lines: [
                  {
                    contents: [{ kind: 'text', text: 'World' }],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {},
      },
      global,
    })

    screenshot()
  })

  it('renders the reference', () => {
    cy.viewport(600, 600)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1',
          instruction: {
            lines: [{ contents: [{ kind: 'text', text: 'Hello' }] }],
          },
          example: null,
          hint: null,
          statement: {
            pages: [
              {
                lines: [
                  {
                    contents: [{ kind: 'text', text: 'World' }],
                  },
                ],
              },
            ],
          },
          reference: { contents: [{ kind: 'text', text: 'Reference' }] },
        },
        imagesUrls: {},
      },
      global,
    })

    cy.get('div.control').last().click()

    screenshot()
  })
})

const image =
  'data:image/png;base64,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'

describe('Images', () => {
  it('renders at 1em', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'image',
                        height: '1em',
                        identifier: 'img1',
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {
          img1: image,
        },
      },
      global,
    })

    screenshot()
  })

  it('renders at 5em', () => {
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
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
                      {
                        kind: 'image',
                        height: '5em',
                        identifier: 'img1',
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {
          img1: image,
        },
      },
      global,
    })

    screenshot()
  })

  it('aligns', () => {
    function makeProps(align: 'left' | 'center' | 'right' | undefined) {
      return {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1' as const,
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'image' as const,
                    height: '3em',
                    align,
                    identifier: 'img1',
                  },
                ],
              },
            ],
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
                        kind: 'image' as const,
                        height: '3em',
                        align,
                        identifier: 'img1',
                      },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {
          img1: image,
        },
      }
    }

    cy.mount(AdaptedExerciseRenderer, { global, props: makeProps(undefined) })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, { global, props: makeProps('left') })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, { global, props: makeProps('center') })
    screenshot()

    cy.mount(AdaptedExerciseRenderer, { global, props: makeProps('right') })
    screenshot()
  })

  it('does not align', () => {
    cy.mount(AdaptedExerciseRenderer, {
      global,
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise: {
          format: 'v1' as const,
          instruction: {
            lines: [
              {
                contents: [
                  {
                    kind: 'image' as const,
                    height: '3em',
                    align: 'right',
                    identifier: 'img1',
                  },
                  { kind: 'text' as const, text: 'blah' },
                ],
              },
            ],
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
                        kind: 'image' as const,
                        height: '3em',
                        align: 'right',
                        identifier: 'img1',
                      },
                      { kind: 'text' as const, text: 'blah' },
                    ],
                  },
                ],
              },
            ],
          },
          reference: null,
        },
        imagesUrls: {
          img1: image,
        },
      },
    })
    screenshot()
  })
})
