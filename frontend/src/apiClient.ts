import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]

export type LatestBatch =
  paths['/api/adaptation/latest-batch']['get']['responses']['200']['content']['application/json']

export type AdaptationStrategy = LatestBatch['strategy']

export type Batches = paths['/api/adaptation/batches']['get']['responses']['200']['content']['application/json']
export type Batch = paths['/api/adaptation/batch/{id}']['get']['responses']['200']['content']['application/json']

export type Adaptation = paths['/api/adaptation/{id}']['get']['responses']['200']['content']['application/json']
export type AdaptedExercise = (Adaptation['adjustments'][number]['assistantResponse'] & { kind: 'success' })['exercise']

export type AnyComponent =
  | AdaptedExercise['instruction']['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['example'], null>['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['hint'], null>['lines'][number]['contents'][number]
  | AdaptedExercise['statement']['pages'][number]['lines'][number]['contents'][number]
  | Exclude<AdaptedExercise['reference'], null>['contents'][number]

type ActiveComponent = AnyComponent & {
  kind: 'multipleChoicesInput' | 'freeTextInput' | 'selectableInput' | 'swappableInput'
}

export type PassiveComponent = Exclude<AnyComponent, ActiveComponent>

export type PureTextContainer = (ActiveComponent & { kind: 'multipleChoicesInput' })['choices'][number]
