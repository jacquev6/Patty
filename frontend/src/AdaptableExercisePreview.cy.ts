import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

import AdaptableExercisePreview, {
  makePreviewAbleExercise_forAdaptation,
  makePreviewAbleExercise_forClassificationOrExtraction,
  makePreviewAbleExercise_forTextbook,
} from './AdaptableExercisePreview.vue'
import type { PreprocessedAdaptation } from './adaptations'
import { ignoreResizeObserverLoopError } from '../e2e-tests/utils'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'

const exercises = {
  'adaptation - in progress': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'inProgress' },
  }),
  'adaptation - LLM error - invalid json': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'error', error: 'invalid-json', parsed: [] },
  }),
  'adaptation - LLM error - not json': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'error', error: 'not-json', text: 'blah' },
  }),
  'adaptation - LLM error - unknown': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'error', error: 'unknown' },
  }),
  'adaptation - LLM error - unexpected': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'error', error: 'not-an-error' } as unknown as PreprocessedAdaptation['status'],
  }),
  'adaptation - unexpected status': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: { kind: 'not-a-status' } as unknown as PreprocessedAdaptation['status'],
  }),
  'adaptation - success': makePreviewAbleExercise_forAdaptation(42, {
    id: 'ad-id',
    input: {
      pageNumber: 37,
      exerciseNumber: '24',
      text: ['This is the full text of the exercise.', 'It has multiple lines.'],
    },
    status: {
      kind: 'success',
      success: 'llm',
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
  }),
  'classification - classification not requested': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    false,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    false,
    null,
    Promise.resolve,
  ),
  'classification - classification in progress - 1': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    false,
    null,
    Promise.resolve,
  ),
  'classification - classification in progress - 2': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    false,
    null,
    Promise.resolve,
  ),
  'classification - classification in progress - 3': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    null,
    Promise.resolve,
  ),
  'classification - classification in progress - 4': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    true,
    null,
    Promise.resolve,
  ),
  'classification - adaptation not requested - 1': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    false,
    null,
    Promise.resolve,
  ),
  'classification - adaptation not requested - 2': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    false,
    null,
    Promise.resolve,
  ),
  'classification - class has no settings': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    true,
    null,
    Promise.resolve,
  ),
  'classification - class had no settings': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    null,
    Promise.resolve,
  ),
  'classification - adaptation in progress': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'inProgress' },
    },
    Promise.resolve,
  ),
  'classification - adaptation with LLM error - not json': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'not-json', text: 'blah' },
    },
    Promise.resolve,
  ),
  'classification - adaptation with LLM error - invalid json': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'invalid-json', parsed: [] },
    },
    Promise.resolve,
  ),
  'classification - adaptation with LLM error - unknown': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'unknown' },
    },
    Promise.resolve,
  ),
  'classification - adaptation with LLM error - unexpected': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'not-an-error' } as unknown as PreprocessedAdaptation['status'],
    },
    Promise.resolve,
  ),
  'classification - adaptation success': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: {
        kind: 'success',
        success: 'llm',
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
    Promise.resolve,
  ),
  'classification - reclassified': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: 'Bob',
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: {
        kind: 'success',
        success: 'llm',
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
    Promise.resolve,
  ),
  'classification - unexpected adaptation status': makePreviewAbleExercise_forClassificationOrExtraction(
    'header text',
    true,
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '24',
      fullText: 'This is the full text of the exercise.\nIt has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    true,
    {
      id: 'ad-id',
      status: { kind: 'not-a-status' } as unknown as PreprocessedAdaptation['status'],
    },
    Promise.resolve,
  ),
  'textbook - classification in progress - 1': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    null,
  ),
  'textbook - classification in progress - 2': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: null,
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    null,
  ),
  'textbook - class has no settings': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: false,
    },
    null,
  ),
  'textbook - class had no settings': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    null,
  ),
  'textbook - adaptation in progress': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'inProgress' },
    },
  ),
  'textbook - adaptation with LLM error - not json': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'not-json', text: 'blah' },
    },
  ),
  'textbook - adaptation with LLM error - invalid json': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'invalid-json', parsed: [] },
    },
  ),
  'textbook - adaptation with LLM error - unknown': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'unknown' },
    },
  ),
  'textbook - adaptation with LLM error - unexpected': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'error', error: 'not-an-error' } as unknown as PreprocessedAdaptation['status'],
    },
  ),
  'textbook - adaptation success': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: {
        kind: 'success',
        success: 'llm',
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
  ),
  'textbook - unexpected adaptation status': makePreviewAbleExercise_forTextbook(
    {
      id: 'ex-id',
      pageNumber: 37,
      exerciseNumber: '32',
      fullText: 'This is the full text of the exercise. It has multiple lines.',
      exerciseClass: 'Blah',
      reclassifiedBy: null,
      exerciseClassHasSettings: true,
    },
    {
      id: 'ad-id',
      status: { kind: 'not-a-status' } as unknown as PreprocessedAdaptation['status'],
    },
  ),
}

describe('AdaptableExercisePreview', () => {
  for (const [title, exercise] of Object.entries(exercises)) {
    it(`looks like this - ${title}`, () => {
      ignoreResizeObserverLoopError()
      setActivePinia(createPinia())
      useIdentifiedUserStore().identifier = 'Alice'
      useAuthenticationTokenStore().set('1234567890abcdef', new Date(Date.now() + 1000 * 60 * 60 * 24))
      cy.viewport(1000, 500)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      cy.mount(AdaptableExercisePreview as any, {
        props: {
          headerLevel: 2,
          exercise,
          showPageAndExercise: exercise.kind !== 'textbook',
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
