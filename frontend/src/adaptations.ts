import type { Adaptation as ApiAdaptation, AdaptedExercise } from './apiClient'

export type PreprocessedAdaptation = {
  id: string
  createdBy: string
  classificationBatchId: string | null
  adaptationBatchId: string | null
  strategy: ApiAdaptation['strategy']
  input: { pageNumber: number | null; exerciseNumber: string | null; text: string[] }
  adjustmentPrompts: string[]
  rawLlmConversations: ApiAdaptation['rawLlmConversations']
  removedFromTextbook: boolean
  llmStatus:
    | {
        kind: 'inProgress'
      }
    | {
        kind: 'error'
        error: 'invalid-json'
        parsed: unknown
      }
    | {
        kind: 'error'
        error: 'not-json'
        text: string
      }
    | {
        kind: 'error'
        error: 'unknown'
      }
    | {
        kind: 'success'
        adaptedExercise: AdaptedExercise
      }
  status:
    | {
        kind: 'inProgress'
      }
    | {
        kind: 'error'
        error: 'invalid-json'
        parsed: unknown
      }
    | {
        kind: 'error'
        error: 'not-json'
        text: string
      }
    | {
        kind: 'error'
        error: 'unknown'
      }
    | {
        kind: 'success'
        success: 'llm' | 'manual'
        adaptedExercise: AdaptedExercise
      }
}

export function preprocess(adaptation: ApiAdaptation): PreprocessedAdaptation {
  function makeLlmStatus(
    response: ApiAdaptation['adjustments'][number]['assistantResponse'],
  ): PreprocessedAdaptation['llmStatus'] {
    // @todo Consider using https://github.com/gvergnaud/ts-pattern everywhere exhaustive matching is expected (git grep never)
    if (response.kind === 'success') {
      return { kind: 'success', adaptedExercise: response.exercise }
    } else if (response.kind === 'error' && response.error === 'invalid-json') {
      return { kind: 'error', error: 'invalid-json', parsed: response.parsed }
    } else if (response.kind === 'error' && response.error === 'not-json') {
      return { kind: 'error', error: 'not-json', text: response.text }
    } else if (response.kind === 'error' && response.error === 'unknown') {
      return { kind: 'error', error: 'unknown' }
    } else {
      return ((r: never) => r)(response)
    }
  }

  const llmStatus = ((): PreprocessedAdaptation['llmStatus'] => {
    if (adaptation.adjustments.length > 0) {
      const lastAdjustment = adaptation.adjustments[adaptation.adjustments.length - 1]
      return makeLlmStatus(lastAdjustment.assistantResponse)
    } else if (adaptation.initialAssistantResponse !== null) {
      return makeLlmStatus(adaptation.initialAssistantResponse)
    } else {
      return { kind: 'inProgress' }
    }
  })()

  const status = ((): PreprocessedAdaptation['status'] => {
    if (adaptation.manualEdit !== null) {
      return { kind: 'success', success: 'manual', adaptedExercise: adaptation.manualEdit }
    } else if (llmStatus.kind === 'success') {
      return { ...llmStatus, success: 'llm' }
    } else {
      return llmStatus
    }
  })()

  return {
    id: adaptation.id,
    createdBy: adaptation.createdBy,
    classificationBatchId: adaptation.classificationBatchId,
    adaptationBatchId: adaptation.adaptationBatchId,
    strategy: adaptation.strategy,
    input: {
      pageNumber: adaptation.input.pageNumber,
      exerciseNumber: adaptation.input.exerciseNumber,
      text: adaptation.input.text.split('\n'),
    },
    adjustmentPrompts: adaptation.adjustments.map((adjustment) => adjustment.userPrompt),
    rawLlmConversations: adaptation.rawLlmConversations,
    removedFromTextbook: adaptation.removedFromTextbook,
    llmStatus,
    status,
  }
}
