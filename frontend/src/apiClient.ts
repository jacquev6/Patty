import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]

export type Adaptation = paths['/api/adaptation/{id}']['get']['responses']['200']['content']['application/json']
export type AdaptedExercise = Exclude<Adaptation['steps'][number]['adaptedExercise'], null>
export type Line = AdaptedExercise['wording']['pages'][number]['lines'][number]
export type Component = Line['contents'][number]
