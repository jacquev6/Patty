import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]

export type LatestBatch =
  paths['/api/adaptation/latest-batch']['get']['responses']['200']['content']['application/json']

export type AdaptationStrategy = LatestBatch['strategy']

export type Textbooks = paths['/api/adaptation/textbooks']['get']['responses']['200']['content']['application/json']
export type Textbook =
  paths['/api/adaptation/textbook/{id}']['get']['responses']['200']['content']['application/json']['textbook']

export type Batches = paths['/api/adaptation/batches']['get']['responses']['200']['content']['application/json']
export type Batch = paths['/api/adaptation/batch/{id}']['get']['responses']['200']['content']['application/json']

export type Adaptation = paths['/api/adaptation/{id}']['get']['responses']['200']['content']['application/json']
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
