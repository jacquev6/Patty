import createClient from 'openapi-fetch'

import type { paths } from './openapi'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'

export function useAuthenticationClient() {
  return createClient<Pick<paths, '/api/token'>>()
}

export function useAuthenticatedClient() {
  const authenticationTokenStore = useAuthenticationTokenStore()

  return createClient<Omit<paths, '/api/token'>>({
    headers: { Authorization: `Bearer ${authenticationTokenStore.token}` },
  })
}

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]

export type LatestAdaptationBatch =
  paths['/api/latest-adaptation-batch']['get']['responses']['200']['content']['application/json']

export type AdaptationStrategy = LatestAdaptationBatch['strategy']

export type Textbooks = paths['/api/textbooks']['get']['responses']['200']['content']['application/json']
export type Textbook =
  paths['/api/textbooks/{id}']['get']['responses']['200']['content']['application/json']['textbook']

export type ClassificationBatch =
  paths['/api/classification-batches/{id}']['get']['responses']['200']['content']['application/json']

export type AdaptationBatches =
  paths['/api/adaptation-batches']['get']['responses']['200']['content']['application/json']
export type AdaptationBatch =
  paths['/api/adaptation-batches/{id}']['get']['responses']['200']['content']['application/json']

export type Adaptation = paths['/api/adaptations/{id}']['get']['responses']['200']['content']['application/json']
export type AdaptedExercise = (Adaptation['adjustments'][number]['assistantResponse'] & { kind: 'success' })['exercise']

export type ActiveEditableTextInput = {
  kind: 'activeEditableTextInput'
  contents: PlainText[]
}

export type AnyComponent =
  | AdaptedExercise['instruction']['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['example'], null>['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['hint'], null>['lines'][number]['contents'][number]
  | AdaptedExercise['statement']['pages'][number]['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['reference'], null>['contents'][number]
  | ActiveEditableTextInput

export type PlainText = AnyComponent & { kind: 'text' | 'whitespace' }
export type FormattedText = AnyComponent & { kind: 'text' | 'whitespace' | 'arrow' | 'formatted' }
export type PassiveComponent = AnyComponent & { kind: 'text' | 'whitespace' | 'arrow' | 'formatted' | 'choice' }
