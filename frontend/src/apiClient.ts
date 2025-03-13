import createClient from 'openapi-fetch'

import type { paths } from './openapi'

console.log('Creating API client')
const apiClient = createClient<paths>()

export function useApiClient() {
  return apiClient
}

type LlmModel = paths['/api/tokenization']['post']['requestBody']['content']['application/json']['llm_model']
type MistralaiModel = LlmModel & { provider: 'mistralai' }
type OpenaiModel = LlmModel & { provider: 'openai' }

export type MistralaiModelName = MistralaiModel['model']
export type OpenaiModelName = OpenaiModel['model']
export type Tokenization = paths['/api/tokenization/{id}']['get']['responses']['200']['content']['application/json']
