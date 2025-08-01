import AdaptedExerciseRenderer from './AdaptedExerciseRenderer.vue'
import TriColorLines from './TriColorLines.vue'
import assert from '@/assert'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  if (!Cypress.config('isInteractive')) {
    const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
    screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
    const name = `${baseName}-${screenshotsCounts[baseName]}`
    cy.compareSnapshot(name)
  }
}

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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
    })
    cy.get('@input').click()
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
      },
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
      },
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
      },
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
      },
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

  it('refuses new lines', () => {
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
      },
    })

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').type('Hello{enter}world')
    cy.get('br').should('not.exist')
    cy.get('@input').should('have.text', 'Helloworld')
  })

  it('allows navigating exercise pages using arrow keys', () => {
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
      },
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
    cy.get('@input').type('{leftArrow}{leftArrow}ONE') // Arrows are ignored
    cy.get('p').should('have.text', 'Page 1 OneONE')
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
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
      },
    })

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
      },
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
      },
    })
    screenshot()
  })
})

describe('TriColorLines', () => {
  it('renders lines in alternating colors', () => {
    cy.viewport(180, 340)

    cy.mount(TriColorLines, {
      slots: {
        default:
          '<p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p><p><span class="tricolorable">Blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span> <span class="tricolorable">blah</span><span class="tricolorable">.</span></p>',
      },
    })

    screenshot()
  })

  it('warns about nested tricolorables', () => {
    cy.viewport(300, 110)

    cy.mount(TriColorLines, {
      slots: {
        default: '<p><span class="tricolorable">B<span><span class="tricolorable">la</span></span>h</span></p>',
      },
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
      },
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
      },
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
      },
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
      },
    })

    screenshot()
    cy.get('[data-cy="freeTextInput"]').eq(0).as('input')
    cy.get('@input').focus().type('{end}')
    screenshot()
    cy.get('@input').type('{backspace}eee.')
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
      },
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
      },
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
      },
    })

    cy.get('div.control').last().click()

    screenshot()
  })
})
