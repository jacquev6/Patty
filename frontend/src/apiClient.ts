import createClient from 'openapi-fetch'

import type { paths } from './openapi'

console.log('Creating API client')
const apiClient = createClient<paths>()

export function useApiClient() {
  return apiClient
}

type MistralaiPostTokenizationRequest =
  paths['/api/tokenization']['post']['requestBody']['content']['application/json'] & { llm_provider: 'mistralai' }
type OpenaiPostTokenizationRequest =
  paths['/api/tokenization']['post']['requestBody']['content']['application/json'] & { llm_provider: 'openai' }

export type MistralaiModelName = MistralaiPostTokenizationRequest['mistralai_model']
export type OpenaiModelName = OpenaiPostTokenizationRequest['openai_model']
export type Tokenization = paths['/api/tokenization/{id}']['get']['responses']['200']['content']['application/json']
