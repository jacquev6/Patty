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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
      approved: null,
    },
    imagesUrls: {},
  },
  'adaptation - success - textually-numbered exercise': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: 'Not a number',
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
      approved: null,
    },
    imagesUrls: {},
  },
  'classification - classification not requested': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: { kind: 'notRequested' },
    imagesUrls: {},
  },
  'classification - classification in progress': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'inProgress' },
    adaptationStatus: { kind: 'notRequested' },
    imagesUrls: {},
  },
  'classification - adaptation not requested - 1': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    imagesUrls: {},
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - adaptation not requested - 2': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    imagesUrls: {},
    adaptationStatus: { kind: 'notRequested' },
  },
  'classification - class has no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    adaptationStatus: { kind: 'notStarted' },
    imagesUrls: {},
  },
  'classification - class had no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: { kind: 'notStarted' },
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
      approved: null,
    },
    imagesUrls: {},
  },
  'classification - adaptation success - textually-numbered exercise': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: 'Not a number',
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
      approved: null,
    },
    imagesUrls: {},
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
      approved: null,
    },
    imagesUrls: {},
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
    imagesUrls: {},
  },
  'extraction - classification not requested': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '24',
    fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
    classificationStatus: { kind: 'notRequested' },
    adaptationStatus: { kind: 'notRequested' },
    imagesUrls: {},
  },
  'extraction - success': {
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
      approved: null,
    },
    imagesUrls: {},
  },
  'extraction - success - textually-numbered exercise': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: 'Not a number',
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
      approved: null,
    },
    imagesUrls: {},
  },
  'textbook - classification in progress': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'inProgress' },
    adaptationStatus: { kind: 'notStarted' },
    imagesUrls: {},
  },
  'textbook - class has no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: false },
    adaptationStatus: { kind: 'notStarted' },
    imagesUrls: {},
  },
  'textbook - class had no settings': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: '32',
    fullText: 'This is the full text of the exercise. It has multiple lines.',
    classificationStatus: { kind: 'byModel', exerciseClass: 'Blah', classHasSettings: true },
    adaptationStatus: { kind: 'notStarted' },
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
    imagesUrls: {},
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
      approved: null,
    },
    imagesUrls: {},
  },
  'textbook - adaptation success - textually-numbered exercise': {
    id: 'ex-id',
    pageNumber: 37,
    exerciseNumber: 'Not a number',
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
      approved: null,
    },
    imagesUrls: {},
  },
  'textbook - adaptation success - approved': {
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
      approved: {
        by: 'Bob',
        at: '2024-01-02T12:34:56Z',
      },
    },
    imagesUrls: {},
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
    imagesUrls: {},
  },
}

describe('AdaptableExercisePreview', () => {
  for (const [title, exercise] of Object.entries(exercises)) {
    const [context, index] = (() => {
      if (title.startsWith('adaptation - ')) {
        return ['adaptation', 42] as const
      } else if (title.startsWith('classification - ')) {
        return ['classification', 42] as const
      } else if (title.startsWith('extraction - ')) {
        return ['extraction', 42] as const
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
      cy.viewport(1200, 500)
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
