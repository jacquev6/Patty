import SequenceComponent from './components/SequenceComponent.vue'
import MultipleChoicesInput from './components/MultipleChoicesInput.vue'
import SelectableInput from './components/SelectableInput.vue'
import FreeTextInput from './components/FreeTextInput.vue'
import AdaptedExerciseRenderer from './AdaptedExerciseRenderer.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  const baseName = Cypress.currentTest.titlePath.join(' -- ')
  screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
  const name = `${baseName} -- ${screenshotsCounts[baseName]}`
  cy.screenshot(name)
}

describe('SequenceComponent', () => {
  beforeEach(console.clear)

  it('renders plain text and whitespace', () => {
    cy.viewport(180, 40)

    cy.mount(SequenceComponent, {
      props: {
        kind: 'sequence',
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
        vertical: false,
      },
    })

    screenshot()
  })

  it('renders formatting', () => {
    cy.viewport(270, 40)

    cy.mount(SequenceComponent, {
      props: {
        kind: 'sequence',
        contents: [
          {
            kind: 'sequence',
            contents: [{ kind: 'text', text: 'bold' }],
            bold: true,
            italic: false,
            highlighted: null,
            boxed: false,
            vertical: false,
          },
          { kind: 'whitespace' },
          {
            kind: 'sequence',
            contents: [{ kind: 'text', text: 'italic' }],
            bold: false,
            italic: true,
            highlighted: null,
            boxed: false,
            vertical: false,
          },
          { kind: 'whitespace' },
          {
            kind: 'sequence',
            contents: [{ kind: 'text', text: 'highlighted' }],
            bold: false,
            italic: false,
            highlighted: 'yellow',
            boxed: false,
            vertical: false,
          },
          { kind: 'whitespace' },
          {
            kind: 'sequence',
            contents: [{ kind: 'text', text: 'boxed' }],
            bold: false,
            italic: false,
            highlighted: null,
            boxed: true,
            vertical: false,
          },
        ],
        bold: false,
        italic: false,
        highlighted: null,
        boxed: false,
        vertical: false,
      },
    })

    screenshot()
  })
})

describe('SelectableInput', () => {
  beforeEach(console.clear)

  it('changes color on click', () => {
    cy.viewport(100, 40)

    cy.mount(SelectableInput, {
      props: {
        kind: 'selectableInput',
        contents: {
          contents: [
            { kind: 'text', text: 'Click' },
            { kind: 'whitespace' },
            { kind: 'text', text: 'us' },
            { kind: 'text', text: '!' },
          ],
        },
        colors: ['rgb(255, 0, 0)', 'rgb(0, 128, 0)'],
        boxed: false,
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
})

describe('FreeTextInput', () => {
  beforeEach(console.clear)

  it('accepts text input', () => {
    cy.viewport(150, 40)

    cy.mount(FreeTextInput, { props: { kind: 'freeTextInput' } })

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
    cy.mount(FreeTextInput, { props: { kind: 'freeTextInput' } })

    cy.get('[data-cy="freeTextInput"]').as('input')
    cy.get('@input').type('Hello{enter}world')
    cy.get('br').should('not.exist')
    cy.get('@input').should('have.text', 'Helloworld')
  })
})

describe('MultipleChoicesInput', () => {
  beforeEach(console.clear)

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
    cy.viewport(200, 130)

    cy.mount(MultipleChoicesInput, { props: { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false } })

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
    cy.mount(MultipleChoicesInput, { props: { kind: 'multipleChoicesInput', choices, showChoicesByDefault: false } })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('[data-cy="choice0"]').should('not.exist')
    cy.get('@input').click()
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="backdrop"]').click()
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('closes choices on click on main span', () => {
    cy.mount(MultipleChoicesInput, { props: { kind: 'multipleChoicesInput', choices, showChoicesByDefault: true } })

    cy.get('[data-cy="multipleChoicesInput"]').as('input')
    cy.get('[data-cy="choice0"]').should('exist')
    cy.get('[data-cy="backdrop"]').should('not.exist')
    cy.get('@input').click()
    cy.get('@input').should('have.text', '....')
    cy.get('[data-cy="choice0"]').should('not.exist')
  })

  it('moves next lines down', () => {
    cy.viewport(300, 270)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        adaptedExercise: {
          format: 'v1',
          instructions: {
            lines: [],
          },
          wording: {
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
          references: null,
        },
      },
    })

    screenshot()
  })

  it('does not render choices over the page navigation controls', () => {
    cy.viewport(300, 270)

    cy.mount(AdaptedExerciseRenderer, {
      props: {
        adaptedExercise: {
          format: 'v1',
          instructions: {
            lines: [],
          },
          wording: {
            pages: [
              {
                lines: [
                  {
                    contents: [{ kind: 'multipleChoicesInput', choices, showChoicesByDefault: true }],
                  },
                  {
                    contents: [
                      { kind: 'text', text: 'Blaaaaaaaaaaaaaaaaaah' },
                      { kind: 'multipleChoicesInput', choices, showChoicesByDefault: true },
                    ],
                  },
                ],
              },
            ],
          },
          references: null,
        },
      },
    })

    screenshot()
  })
})
