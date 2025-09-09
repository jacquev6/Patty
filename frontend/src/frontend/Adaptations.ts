import { match } from 'ts-pattern'
import type { Adaptation as ApiAdaptation, AdaptedExercise } from './ApiClient'

export type PreprocessedAdaptation = {
  id: string
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
    return match(response)
      .returnType<PreprocessedAdaptation['llmStatus']>()
      .with({ kind: 'success' }, (r) => ({ kind: 'success', adaptedExercise: r.exercise }))
      .with({ kind: 'error', error: 'invalid-json' }, (r) => ({
        kind: 'error',
        error: 'invalid-json',
        parsed: r.parsed,
      }))
      .with({ kind: 'error', error: 'not-json' }, (r) => ({ kind: 'error', error: 'not-json', text: r.text }))
      .with({ kind: 'error', error: 'unknown' }, () => ({ kind: 'error', error: 'unknown' }))
      .exhaustive()
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
