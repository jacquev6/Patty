import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]

export type LatestBatch =
  paths['/api/adaptation/latest-batch']['get']['responses']['200']['content']['application/json']

export type AdaptationStrategy =
  paths['/api/adaptation/latest-strategy']['get']['responses']['200']['content']['application/json']

export type AdaptationInput =
  paths['/api/adaptation/latest-input']['get']['responses']['200']['content']['application/json']

export type Batch = paths['/api/adaptation/batch/{id}']['get']['responses']['200']['content']['application/json']

export type Adaptation = paths['/api/adaptation/{id}']['get']['responses']['200']['content']['application/json']
export type AdaptedExercise = Exclude<Adaptation['initialAssistantResponse'], null>
type InstructionComponent = AdaptedExercise['instruction']['lines'][number]['contents'][number]
type StatementComponent = AdaptedExercise['statement']['pages'][number]['lines'][number]['contents'][number]
export type Component = InstructionComponent | StatementComponent

export type PureTextContainer = (StatementComponent & { kind: 'multipleChoicesInput' })['choices'][number]
