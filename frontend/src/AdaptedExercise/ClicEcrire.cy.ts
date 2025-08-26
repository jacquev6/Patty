import type { AdaptedExercise } from '@/apiClient'
import AdaptedExerciseRenderer from './AdaptedExerciseRenderer.vue'

const yellow = '#ffff00'

const adaptedExercise: AdaptedExercise = {
  format: 'v2',
  steps: [
    {
      instruction: {
        lines: [
          {
            contents: [
              {
                kind: 'formatted',
                contents: [
                  { kind: 'text', text: 'Select' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'some' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'words' },
                  { kind: 'text', text: '.' },
                ],
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
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Alpha' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Bravo' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Charlie' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Delta' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Echo' }],
                  },
                  { kind: 'text', text: '.' },
                ],
              },
              {
                contents: [
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Foxtrot' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Golf' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Hotel' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'India' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Juliet' }],
                  },
                  { kind: 'text', text: '.' },
                ],
              },
            ],
          },
          {
            lines: [
              {
                contents: [
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Kilo' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Lima' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Mike' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'November' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: [yellow],
                    contents: [{ kind: 'text', text: 'Oscar' }],
                  },
                  { kind: 'text', text: '.' },
                ],
              },
            ],
          },
        ],
      },
    },
    {
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Comment' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'those' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'words' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: null,
      hint: null,
      statement: {
        generated: {
          items: {
            kind: 'selectableInput',
            colorIndex: 1,
          },
          itemsPerPage: 3,
          template: {
            contents: [
              { kind: 'itemPlaceholder' },
              { kind: 'whitespace' },
              { kind: 'arrow' },
              { kind: 'whitespace' },
              { kind: 'freeTextInput' },
            ],
          },
        },
      },
    },
  ],
  reference: null,
}

describe('An exercise of type "ClicEcrire"', () => {
  beforeEach(() => {
    cy.viewport(800, 600)
    cy.mount(AdaptedExerciseRenderer, {
      props: {
        navigateUsingArrowKeys: true,
        adaptedExercise,
      },
    })
  })

  it('renders a single empty ad-hoc page when no words have been selected', () => {
    cy.get('.control').eq(1).click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('not.exist')
  })

  it('renders an ad-hoc page with a single word selected from the first line on the first page', () => {
    cy.get('[data-cy="selectableInput"]:contains("Bravo")').click()
    cy.get('.control').eq(1).click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 1).parent().should('contain', 'Bravo')
  })

  it('renders an ad-hoc page with a single word selected from the second line on the first page', () => {
    cy.get('[data-cy="selectableInput"]:contains("Hotel")').click()
    cy.get('.control').eq(1).click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 1).parent().should('contain', 'Hotel')
  })

  it('renders an ad-hoc page with a single word selected from the second page', () => {
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="selectableInput"]:contains("Oscar")').click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 1).parent().should('contain', 'Oscar')
  })

  it('renders a single ad-hoc page with three selected words', () => {
    cy.get('[data-cy="selectableInput"]:contains("Juliet")').click()
    cy.get('[data-cy="selectableInput"]:contains("Alpha")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="selectableInput"]:contains("November")').click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 3)
    cy.get('[data-cy="freeTextInput"]').eq(0).parent().should('contain', 'Alpha')
    cy.get('[data-cy="freeTextInput"]').eq(1).parent().should('contain', 'Juliet')
    cy.get('[data-cy="freeTextInput"]').eq(2).parent().should('contain', 'November')
  })

  it('renders two ad-hoc pages with five selected words', () => {
    cy.get('[data-cy="selectableInput"]:contains("Juliet")').click()
    cy.get('[data-cy="selectableInput"]:contains("Alpha")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="selectableInput"]:contains("Lima")').click()
    cy.get('[data-cy="selectableInput"]:contains("November")').click()
    cy.get('[data-cy="selectableInput"]:contains("Kilo")').click()
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 3)
    cy.get('[data-cy="freeTextInput"]').eq(0).parent().should('contain', 'Alpha')
    cy.get('[data-cy="freeTextInput"]').eq(1).parent().should('contain', 'Juliet')
    cy.get('[data-cy="freeTextInput"]').eq(2).parent().should('contain', 'Kilo')
    cy.get('.control').eq(1).click()
    cy.get(':contains("Comment those words.")').should('exist')
    cy.get('[data-cy="freeTextInput"]').should('have.length', 2)
    cy.get('[data-cy="freeTextInput"]').eq(0).parent().should('contain', 'Lima')
    cy.get('[data-cy="freeTextInput"]').eq(1).parent().should('contain', 'November')
  })

  it('keeps comments associated to words when selection changes', () => {
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="selectableInput"]:contains("Kilo")').click()
    cy.get('[data-cy="selectableInput"]:contains("Oscar")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').should('have.length', 2)
    cy.get('p:contains("Kilo") [data-cy="freeTextInput"]').type('KILO')
    cy.get('p:contains("Oscar") [data-cy="freeTextInput"]').type('OSCAR')
    cy.get('.control').eq(0).click()
    cy.get('[data-cy="selectableInput"]:contains("Mike")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').should('have.length', 3)
    cy.get('p:contains("Kilo"):contains("KILO")').should('exist')
    cy.get('p:contains("Oscar"):contains("OSCAR")').should('exist')
    cy.get('p:contains("Mike") [data-cy="freeTextInput"]').type('MIKE')
    cy.get('.control').eq(0).click()
    cy.get('[data-cy="selectableInput"]:contains("Mike")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').should('have.length', 2)
    cy.get('p:contains("Kilo"):contains("KILO")').should('exist')
    cy.get('p:contains("Oscar"):contains("OSCAR")').should('exist')
    cy.get('.control').eq(0).click()
    cy.get('[data-cy="selectableInput"]:contains("November")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').should('have.length', 3)
    cy.get('p:contains("Kilo"):contains("KILO")').should('exist')
    cy.get('p:contains("Oscar"):contains("OSCAR")').should('exist')
    cy.get('.control').eq(0).click()
    cy.get('[data-cy="selectableInput"]:contains("November")').click()
    cy.get('[data-cy="selectableInput"]:contains("Mike")').click()
    cy.get('.control').eq(1).click()
    cy.get('[data-cy="freeTextInput"]').should('have.length', 3)
    cy.get('p:contains("Kilo"):contains("KILO")').should('exist')
    cy.get('p:contains("Mike"):contains("MIKE")').should('exist')
    cy.get('p:contains("Oscar"):contains("OSCAR")').should('exist')
  })
})
