import createClient from 'openapi-fetch'

import type { paths } from './openapi'

console.log('Creating API client')
const apiClient = createClient<paths>()

export function useApiClient() {
  return apiClient
}

export type MistralModelName =
  paths['/api/tokenization']['post']['requestBody']['content']['application/json']['mistral_model']
export type Tokenization = paths['/api/tokenization/{id}']['get']['responses']['200']['content']['application/json']
