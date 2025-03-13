import createClient from 'openapi-fetch'

import type { paths } from './openapi'

export const client = createClient<paths>()

export type PostTokenizationRequest = paths['/api/tokenization']['post']['requestBody']['content']['application/json']
export type Tokenization = paths['/api/tokenization/{id}']['get']['responses']['200']['content']['application/json']
