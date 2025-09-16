import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

import AdaptableExercisePreview, { type PreviewableExercise } from './AdaptableExercisePreview.vue'
import { ignoreResizeObserverLoopError } from '@/../e2e-tests/utils'
import { useIdentifiedUserStore } from '../basic/IdentifiedUserStore'
import { useAuthenticationTokenStore } from '../basic/AuthenticationTokenStore'

const exercises: Record<string, PreviewableExercise> = {
  'adaptation - in progress': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'inProgress',
      id: 'ad-id',
    },
  },
  'adaptation - LLM error - invalid json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'error',
      error: 'invalid-json',
      parsed: [],
      id: 'ad-id',
    },
  },
  'adaptation - LLM error - not json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'error',
      error: 'not-json',
      text: 'blah',
      id: 'ad-id',
    },
  },
  'adaptation - LLM error - unknown': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'error',
      error: 'unknown',
      id: 'ad-id',
    },
  },
  'adaptation - LLM error - unexpected': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'error',
      error: 'not-an-error',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
  'adaptation - unexpected status': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'not-a-status',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
  'adaptation - success': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: {
      kind: 'success',
      success: 'llm',
      id: 'ad-id',
      adaptedExercise: {
        format: 'v1',
        instruction: {
          lines: [{ contents: [{ kind: 'text', text: 'This is the instructions.' }] }],
        },
        example: null,
        hint: null,
        statement: {
          pages: [
            {
              lines: [{ contents: [{ kind: 'text', text: 'This is the statement.' }] }],
            },
          ],
        },
        reference: null,
      },
    },
  },
  'classification - classification not requested': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - classification in progress - 1': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'inProgress' },
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - adaptation not requested - 1': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - adaptation not requested - 2': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - class has no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    adaptationStatus: { kind: 'notStarted' },
  },
  'classification - class had no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: { kind: 'notStarted' },
  },
  'classification - adaptation in progress': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'inProgress',
      id: 'ad-id',
    },
  },
  'classification - adaptation with LLM error - not json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'not-json',
      text: 'blah',
      id: 'ad-id',
    },
  },
  'classification - adaptation with LLM error - invalid json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'invalid-json',
      parsed: [],
      id: 'ad-id',
    },
  },
  'classification - adaptation with LLM error - unknown': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'unknown',
      id: 'ad-id',
    },
  },
  'classification - adaptation with LLM error - unexpected': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'not-an-error',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
  'classification - adaptation success': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'success',
      success: 'llm',
      id: 'ad-id',
      adaptedExercise: {
        format: 'v1',
        instruction: {
          lines: [{ contents: [{ kind: 'text', text: 'This is the instructions.' }] }],
        },
        example: null,
        hint: null,
        statement: {
          pages: [
            {
              lines: [{ contents: [{ kind: 'text', text: 'This is the statement.' }] }],
            },
          ],
        },
        reference: null,
      },
    },
  },
  'classification - reclassified': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byUser', exerciseClass: 'Blah', by: 'Bob', classHasSettings: true },
    adaptationStatus: {
      kind: 'success',
      success: 'llm',
      id: 'ad-id',
      adaptedExercise: {
        format: 'v1',
        instruction: {
          lines: [{ contents: [{ kind: 'text', text: 'This is the instructions.' }] }],
        },
        example: null,
        hint: null,
        statement: {
          pages: [
            {
              lines: [{ contents: [{ kind: 'text', text: 'This is the statement.' }] }],
            },
          ],
        },
        reference: null,
      },
    },
  },
  'classification - unexpected adaptation status': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'not-a-status',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
  'textbook - classification in progress - 1': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'inProgress' },
    adaptationStatus: { kind: 'notStarted' },
  },
  'textbook - class has no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    adaptationStatus: { kind: 'notStarted' },
  },
  'textbook - class had no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: { kind: 'notStarted' },
  },
  'textbook - adaptation in progress': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'inProgress',
      id: 'ad-id',
    },
  },
  'textbook - adaptation with LLM error - not json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'not-json',
      text: 'blah',
      id: 'ad-id',
    },
  },
  'textbook - adaptation with LLM error - invalid json': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'invalid-json',
      parsed: [],
      id: 'ad-id',
    },
  },
  'textbook - adaptation with LLM error - unknown': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'unknown',
      id: 'ad-id',
    },
  },
  'textbook - adaptation with LLM error - unexpected': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'error',
      error: 'not-an-error',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
  'textbook - adaptation success': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'success',
      success: 'llm',
      id: 'ad-id',
      adaptedExercise: {
        format: 'v1',
        instruction: {
          lines: [{ contents: [{ kind: 'text', text: 'This is the instructions.' }] }],
        },
        example: null,
        hint: null,
        statement: {
          pages: [
            {
              lines: [{ contents: [{ kind: 'text', text: 'This is the statement.' }] }],
            },
          ],
        },
        reference: null,
      },
    },
  },
  'textbook - unexpected adaptation status': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: {
      kind: 'not-a-status',
      id: 'ad-id',
    } as unknown as PreviewableExercise['adaptationStatus'],
  },
}

describe('AdaptableExercisePreview', () => {
  for (const [title, exercise] of Object.entries(exercises)) {
    const [context, index] = (() => {
      if (title.startsWith('adaptation - ')) {
        return ['adaptation', 42] as const
      } else if (title.startsWith('classification - ')) {
        return ['classification', 42] as const
      } else {
        assert(title.startsWith('textbook - '))
        return ['textbookByBatch', null] as const
      }
    })()

    it(`looks like this - ${title}`, () => {
      ignoreResizeObserverLoopError()
      setActivePinia(createPinia())
      useIdentifiedUserStore().identifier = 'Alice'
      useAuthenticationTokenStore().set('1234567890abcdef', new Date(Date.now() + 1000 * 60 * 60 * 24))
      cy.viewport(1000, 500)
      cy.mount(AdaptableExercisePreview, {
        props: {
          headerLevel: 2,
          context,
          index,
          exercise,
        },
        global: {
          plugins: [
            createI18n({ legacy: false, locale: 'en', fallbackLocale: 'en' }),
            createRouter({
              history: createMemoryHistory(),
              routes: [
                {
                  path: '/adaptation-:id',
                  name: 'adaptation',
                  component: { template: '<div>Adaptation</div>' },
                },
                {
                  // Catch-all route so that Cypress paths don't frighten vue-router
                  path: '/:pathMatch(.*)*',
                  component: { template: '<div>404</div>' },
                },
              ],
            }),
          ],
        },
      })
      if (!Cypress.config().isInteractive) {
        cy.compareSnapshot(title.replaceAll(' - ', '-').replaceAll(' ', '_'))
      }
    })
  }
})
