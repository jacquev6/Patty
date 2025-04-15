import type { Adaptation as ApiAdaptation } from './apiClient'

export type PreprocessedAdaptation = {
  id: number
  input: string[]
  status:
    | {
        kind: 'inProgress'
      }
    | {
        kind: 'error'
        error: string
      }
    | {
        kind: 'success'
        adaptedExercise: Exclude<ApiAdaptation['initialAssistantResponse'], null>
      }
}

export function preprocess(adaptation: ApiAdaptation): PreprocessedAdaptation {
  const status = (() => {
    if (adaptation.initialAssistantResponse !== null) {
      // @todo Choose the adaptedExercise as the manualEdit or tha last adjustment
      return { kind: 'success' as const, adaptedExercise: adaptation.initialAssistantResponse }
    } else if (adaptation.initialAssistantError !== null) {
      return { kind: 'error' as const, error: adaptation.initialAssistantError }
    } else {
      return { kind: 'inProgress' as const }
    }
  })()

  return { id: adaptation.id, input: adaptation.input.text.split('\n'), status }
}
