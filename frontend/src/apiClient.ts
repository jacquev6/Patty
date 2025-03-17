import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type LlmModel =
  paths['/api/available-llm-models']['get']['responses']['200']['content']['application/json'][number]
export type Tokenization = paths['/api/tokenization/{id}']['get']['responses']['200']['content']['application/json']
export type Adaptation = paths['/api/adaptation/{id}']['get']['responses']['200']['content']['application/json']
