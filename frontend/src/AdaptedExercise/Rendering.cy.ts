import AdaptedExerciseRenderer from './AdaptedExerciseRenderer.vue'
import FormattedComponent from './components/FormattedComponent.vue'
import FreeTextInput from './components/FreeTextInput.vue'
import MultipleChoicesInput from './components/MultipleChoicesInput.vue'
import SelectableInput from './components/SelectableInput.vue'
import TriColorLines from './TriColorLines.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
  screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
  const name = `${baseName}-${screenshotsCounts[baseName]}-${Cypress.browser.name}`
  cy.compareSnapshot(name)
}

describe('FormattedComponent', () => {
  it('renders plain text and whitespace', () => {
    cy.viewport(200, 70)

    cy.mount(FormattedComponent, {
      props: {
        kind: 'formatted',
        contents: [
          { kind: 'text', text: 'Some' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'casual' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'text' },
          { kind: 'text', text: '.' },
        ],
        bold: false,
        italic: false,
        highlighted: null,
        boxed: false,
        tricolorable: false,
      },
    })

    screenshot()
  })

  it('renders bold', () => {
    cy.viewport(200, 70)
    cy.mount(FormattedComponent, {
      props: {
        kind: 'formatted',
        contents: [
          { kind: 'text', text: 'Bold' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'text' },
          { kind: 'text', text: '.' },
        ],
        bold: true,
        italic: false,
        highlighted: null,
        boxed: false,
        tricolorable: false,
      },
    })
    screenshot()
  })

  it('renders italic', () => {
    cy.viewport(200, 70)
    cy.mount(FormattedComponent, {
      props: {
        kind: 'formatted',
        contents: [
          { kind: 'text', text: 'Italic' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'text' },
          { kind: 'text', text: '.' },
        ],
        bold: false,
        italic: true,
        highlighted: null,
        boxed: false,
        tricolorable: false,
      },
    })
    screenshot()
  })

  it('renders highlighted', () => {
    cy.viewport(200, 70)
    cy.mount(FormattedComponent, {
      props: {
        kind: 'formatted',
        contents: [
          { kind: 'text', text: 'Highlighted' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'text' },
          { kind: 'text', text: '.' },
        ],
        bold: false,
        italic: false,
        highlighted: 'yellow',
        boxed: false,
        tricolorable: false,
      },
    })
    screenshot()
  })

  it('renders boxed', () => {
    cy.viewport(200, 70)
    cy.mount(FormattedComponent, {
      props: {
        kind: 'formatted',
        contents: [
          { kind: 'text', text: 'Boxed' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'text' },
          { kind: 'text', text: '.' },
        ],
        bold: false,
        italic: false,
        highlighted: null,
        boxed: true,
        tricolorable: false,
      },
    })
    screenshot()
  })
})

describe('SelectableInput', () => {
  it('changes color on click', () => {
    cy.viewport(130, 70)

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [
          { kind: 'text', text: 'Click' },
          { kind: 'whitespace' },
          { kind: 'text', text: 'us' },
          { kind: 'text', text: '!' },
        ],
        colors: ['rgb(255, 0, 0)', 'rgb(0, 128, 0)'],
        boxed: false,
        tricolorable: false,
        modelValue: 0,
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
    cy.viewport(130, 70)

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: 'Word' }],
        colors: ['grey'],
        boxed: false,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('[data-cy="selectableInput"]').as('input')
    cy.get('@input').click()
    screenshot()

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: 'Word' }],
        colors: ['grey'],
        boxed: true,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: 'X' }],
        colors: ['grey'],
        boxed: false,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: 'X' }],
        colors: ['grey'],
        boxed: true,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: '.' }],
        colors: ['grey'],
        boxed: false,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('@input').click()
    screenshot()

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: [{ kind: 'text', text: '.' }],
        colors: ['grey'],
        boxed: true,
        tricolorable: false,
        modelValue: 0,
      },
    })
    cy.get('@input').click()
    screenshot()
  })
})

describe('FreeTextInput', () => {
  it('accepts text input', () => {
    cy.viewport(170, 70)

    cy.mount(FreeTextInput, { props: { kind: 'freeTextInput', tricolorable: false, modelValue: '' } })

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
    cy.mount(FreeTextInput, { props: { kind: 'freeTextInput', tricolorable: false, modelValue: '' } })

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').type('Hello{enter}world')
    cy.get('br').should('not.exist')
    cy.get('@input').should('have.text', 'Helloworld')
  })
})

describe('MultipleChoicesInput', () => {
  const choices = [
    {
      contents: [{ kind: 'text' as const, text: 'Alpha' }],
    },
    {
      contents: [{ kind: 'text' as const, text: 'Bravo' }],
    },
    {
      contents: [{ kind: 'text' as const, text: 'Charlie' }],
    },
  ]

  it('selects choices', () => {
    cy.viewport(250, 190)

    cy.mount(MultipleChoicesInput, {
      props: {
        kind: 'multipleChoicesInput',
        choices,
        showChoicesByDefault: false,
        tricolorable: false,
        modelValue: null,
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
    cy.mount(MultipleChoicesInput, {
      props: {
        kind: 'multipleChoicesInput',
        choices,
        showChoicesByDefault: false,
        tricolorable: false,
        modelValue: null,
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
    cy.mount(MultipleChoicesInput, {
      props: {
        kind: 'multipleChoicesInput',
        choices,
        showChoicesByDefault: true,
        tricolorable: false,
        modelValue: null,
      },
    })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="backdrop"]').should('not.exist')
    cy.get('@input').click()
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('moves next lines down', () => {
    cy.viewport(600, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
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
    cy.viewport(543, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
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

describe('AdaptedExerciseRenderer', () => {
  it('supports exercise with zero pages in statement', () => {
    cy.viewport(600, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
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
    cy.viewport(600, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
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
    cy.viewport(600, 550)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
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
