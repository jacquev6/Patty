import type { Adaptation as ApiAdaptation } from './apiClient'
import assert from './assert'

export type PreprocessedAdaptation = {
  id: string
  createdBy: string
  strategy: ApiAdaptation['strategy']
  input: string[]
  adjustmentPrompts: string[]
  rawLlmConversations: ApiAdaptation['rawLlmConversations']
  llmStatus:
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
        success: 'llm' | 'manual'
        adaptedExercise: Exclude<ApiAdaptation['initialAssistantResponse'], null>
      }
}

export function preprocess(adaptation: ApiAdaptation): PreprocessedAdaptation {
  const llmStatus = ((): PreprocessedAdaptation['llmStatus'] => {
    if (adaptation.adjustments.length > 0) {
      const lastAdjustment = adaptation.adjustments[adaptation.adjustments.length - 1]
      if (lastAdjustment.assistantResponse !== null) {
        return { kind: 'success', adaptedExercise: lastAdjustment.assistantResponse }
      } else {
        assert(lastAdjustment.assistantError !== null)
        return { kind: 'error', error: lastAdjustment.assistantError }
      }
    } else if (adaptation.initialAssistantResponse !== null) {
      return { kind: 'success', adaptedExercise: adaptation.initialAssistantResponse }
    } else if (adaptation.initialAssistantError !== null) {
      return { kind: 'error', error: adaptation.initialAssistantError }
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
    strategy: adaptation.strategy,
    input: adaptation.input.text.split('\n'),
    adjustmentPrompts: adaptation.adjustments.map((adjustment) => adjustment.userPrompt),
    rawLlmConversations: adaptation.rawLlmConversations,
    llmStatus,
    status,
  }
}
