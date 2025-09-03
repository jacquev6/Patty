import { createRouter, createWebHashHistory } from 'vue-router'
import _ from 'lodash'

import TextbookExportExercisesList from './ExercisesList.vue'
import TextbookExportExerciseView from './ExerciseView.vue'
import TextbookExportIndexView from './IndexView.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  if (!Cypress.config('isInteractive')) {
    const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
    screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
    const name = `${baseName}-${screenshotsCounts[baseName]}`
    cy.compareSnapshot(name)
  }
}

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      name: 'index',
      path: '/',
      component: TextbookExportIndexView,
    },
    {
      name: 'exercise',
      path: '/exercise/:id',
      component: TextbookExportExerciseView,
    },
  ],
})

const global = { plugins: [router] }

describe('TextbookExportExercisesList', () => {
  beforeEach(() => {
    cy.viewport(500, 260)
  })

  it('renders 4 links', () => {
    cy.mount(TextbookExportExercisesList, {
      props: {
        exercises: _.range(1, 5).map((i) => ({
          kind: 'adapted' as const,
          exerciseId: `P22Ex${i}`,
          exerciseNumber: `${i}`,
        })),
      },
      global,
    })

    cy.get('a').eq(0).should('have.text', 'Exercice 1')
    cy.get('div.control').eq(0).should('have.class', 'disabled')
    cy.get('div.control').eq(1).should('have.class', 'disabled')
    screenshot()
  })

  it('renders 10 links', () => {
    cy.mount(TextbookExportExercisesList, {
      props: {
        exercises: _.range(1, 11).map((i) => ({
          kind: 'adapted' as const,
          exerciseId: `P22Ex${i}`,
          exerciseNumber: `${i}`,
        })),
      },
      global,
    })

    cy.get('a').eq(0).should('have.text', 'Exercice 1')
    cy.get('div.control').eq(0).should('have.class', 'disabled')
    cy.get('div.control').eq(1).should('not.have.class', 'disabled')
    screenshot()

    cy.get('div.control').eq(1).click()
    cy.get('div.control').eq(0).should('not.have.class', 'disabled')
    cy.get('div.control').eq(1).should('have.class', 'disabled')
    screenshot()
  })

  it('renders 100 links', () => {
    cy.mount(TextbookExportExercisesList, {
      props: {
        exercises: _.range(1, 101).map((i) => ({
          kind: 'adapted' as const,
          exerciseId: `P22Ex${i}`,
          exerciseNumber: `${i}`,
        })),
      },
      global,
    })

    cy.get('a').eq(0).should('have.text', 'Exercice 1')
    cy.get('div.control').eq(0).should('have.class', 'disabled')
    cy.get('div.control').eq(1).should('not.have.class', 'disabled')
    screenshot()

    cy.get('div.control').eq(1).click()
    cy.get('div.control').eq(0).should('not.have.class', 'disabled')
    cy.get('div.control').eq(1).should('not.have.class', 'disabled')
    cy.wait(500) // Give time to the "smooth" scrolling
    screenshot()
  })
})
