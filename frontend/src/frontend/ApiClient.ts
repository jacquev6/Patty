import createClient from 'openapi-fetch'

import type { paths } from '@/frontend/openapi'
import { useAuthenticationTokenStore } from './basic/AuthenticationTokenStore'
import assert from '$/assert'

export function useAuthenticationClient() {
  return createClient<Pick<paths, '/api/token'>>()
}

export function useAuthenticatedClient() {
  const authenticationTokenStore = useAuthenticationTokenStore()

  assert(authenticationTokenStore.token !== null)

  return createClient<Omit<paths, '/api/token'>>({
    headers: { Authorization: `Bearer ${authenticationTokenStore.token}` },
  })
}

export type ErrorCaughtByFrontend =
  paths['/api/errors-caught-by-frontend']['get']['responses']['200']['content']['application/json']['errors'][number]

export type ExtractionLlmModel =
  paths['/api/available-extraction-llm-models']['get']['responses']['200']['content']['application/json'][number]
export type ExtractionStrategy =
  paths['/api/latest-extraction-strategy']['get']['responses']['200']['content']['application/json']

export type AdaptationLlmModel =
  paths['/api/available-adaptation-llm-models']['get']['responses']['200']['content']['application/json'][number]
export type BaseAdaptationBatch =
  paths['/api/base-adaptation-batch']['get']['responses']['200']['content']['application/json']

export type AdaptationStrategy = BaseAdaptationBatch['strategy']

export type Textbooks = paths['/api/textbooks']['get']['responses']['200']['content']['application/json']
export type Textbook =
  paths['/api/textbooks/{id}']['get']['responses']['200']['content']['application/json']['textbook']

export type ExtractionBatches =
  paths['/api/extraction-batches']['get']['responses']['200']['content']['application/json']
export type ExtractionBatch =
  paths['/api/extraction-batches/{id}']['get']['responses']['200']['content']['application/json']

export type ClassificationBatches =
  paths['/api/classification-batches']['get']['responses']['200']['content']['application/json']
export type ClassificationBatch =
  paths['/api/classification-batches/{id}']['get']['responses']['200']['content']['application/json']

export type AdaptationBatches =
  paths['/api/adaptation-batches']['get']['responses']['200']['content']['application/json']
export type AdaptationBatch =
  paths['/api/adaptation-batches/{id}']['get']['responses']['200']['content']['application/json']

export type Adaptation = paths['/api/adaptations/{id}']['get']['responses']['200']['content']['application/json']
export type AdaptedExercise = (Adaptation['lastAssistantResponse'] & { kind: 'success' })['exercise']
export type AdaptedExerciseV2 = AdaptedExercise & { format: 'v2' }
