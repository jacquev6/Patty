/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */

export interface paths {
  '/api/available-llm-models': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Available Llm Models */
    get: operations['get_available_llm_models_api_available_llm_models_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/latest-strategy': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Latest Strategy */
    get: operations['get_latest_strategy_api_adaptation_latest_strategy_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/latest-input': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Latest Input */
    get: operations['get_latest_input_api_adaptation_latest_input_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /** Post Adaptation */
    post: operations['post_adaptation_api_adaptation_post']
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/{id}': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Adaptation */
    get: operations['get_adaptation_api_adaptation__id__get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/{id}/adjustment': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /** Post Adaptation Adjustment */
    post: operations['post_adaptation_adjustment_api_adaptation__id__adjustment_post']
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/{id}/last-step': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post?: never
    /** Delete Adaptation Last Step */
    delete: operations['delete_adaptation_last_step_api_adaptation__id__last_step_delete']
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/adaptation/{id}/manual-edit': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    /** Put Adaptation Manual Edit */
    put: operations['put_adaptation_manual_edit_api_adaptation__id__manual_edit_put']
    post?: never
    /** Delete Adaptation Manual Edit */
    delete: operations['delete_adaptation_manual_edit_api_adaptation__id__manual_edit_delete']
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
}
export type webhooks = Record<string, never>
export interface components {
  schemas: {
    /** Adaptation */
    Adaptation: {
      /** Id */
      id: number
      /** Llmmodel */
      llmModel:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** Steps */
      steps: (components['schemas']['InitialStep'] | components['schemas']['AdjustmentStep'])[]
      manualEdit: components['schemas']['Exercise-Output'] | null
    }
    /** AdjustmentStep */
    AdjustmentStep: {
      /**
       * Kind
       * @constant
       */
      kind: 'adjustment'
      /** Userprompt */
      userPrompt: string
      /** Messages */
      messages: (
        | components['schemas']['UserMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['AssistantMessage_ProseAndExercise_']
      )[]
      /** Assistantprose */
      assistantProse: string
      adaptedExercise: components['schemas']['Exercise-Output'] | null
    }
    /** AnySequence */
    'AnySequence-Input': {
      /**
       * Kind
       * @constant
       */
      kind: 'sequence'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Input']
        | components['schemas']['SelectableInput-Input']
        | components['schemas']['AnySequence-Input']
      )[]
      /** Bold */
      bold: boolean
      /** Italic */
      italic: boolean
      /** Highlighted */
      highlighted: string | null
      /** Boxed */
      boxed: boolean
      /** Vertical */
      vertical: boolean
    }
    /** AnySequence */
    'AnySequence-Output': {
      /**
       * Kind
       * @constant
       */
      kind: 'sequence'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Output']
        | components['schemas']['SelectableInput-Output']
        | components['schemas']['AnySequence-Output']
      )[]
      /** Bold */
      bold: boolean
      /** Italic */
      italic: boolean
      /** Highlighted */
      highlighted: string | null
      /** Boxed */
      boxed: boolean
      /** Vertical */
      vertical: boolean
    }
    /** Arrow */
    Arrow: {
      /**
       * Kind
       * @constant
       */
      kind: 'arrow'
    }
    /** AssistantMessage[ProseAndExercise] */
    AssistantMessage_ProseAndExercise_: {
      /**
       * Role
       * @default assistant
       * @constant
       */
      role: 'assistant'
      message: components['schemas']['ProseAndExercise']
    }
    /** DummyModel */
    DummyModel: {
      /**
       * Provider
       * @default dummy
       * @constant
       */
      provider: 'dummy'
      /**
       * Name
       * @enum {string}
       */
      name: 'dummy-1' | 'dummy-2' | 'dummy-3'
    }
    /** Exercise */
    'Exercise-Input': {
      /**
       * Format
       * @constant
       */
      format: 'v1'
      instructions: components['schemas']['Page_Union_Text__Whitespace__Arrow__PassiveSequence__-Input']
      wording: components['schemas']['Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input']
      references: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Input'] | null
    }
    /** Exercise */
    'Exercise-Output': {
      /**
       * Format
       * @constant
       */
      format: 'v1'
      instructions: components['schemas']['Page_Union_Text__Whitespace__Arrow__PassiveSequence__-Output']
      wording: components['schemas']['Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output']
      references: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Output'] | null
    }
    /** FreeTextInput */
    FreeTextInput: {
      /**
       * Kind
       * @constant
       */
      kind: 'freeTextInput'
    }
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components['schemas']['ValidationError'][]
    }
    /** InitialStep */
    InitialStep: {
      /**
       * Kind
       * @constant
       */
      kind: 'initial'
      /** Systemprompt */
      systemPrompt: string
      /** Inputtext */
      inputText: string
      /** Messages */
      messages: (
        | components['schemas']['UserMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['AssistantMessage_ProseAndExercise_']
      )[]
      /** Assistantprose */
      assistantProse: string
      adaptedExercise: components['schemas']['Exercise-Output'] | null
    }
    /** Input */
    Input: {
      /** Id */
      id: number
      /** Text */
      text: string
    }
    /** Line[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Input']
        | components['schemas']['SelectableInput-Input']
        | components['schemas']['AnySequence-Input']
      )[]
    }
    /** Line[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Output']
        | components['schemas']['SelectableInput-Output']
        | components['schemas']['AnySequence-Output']
      )[]
    }
    /** Line[Union[Text, Whitespace, Arrow, PassiveSequence]] */
    'Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Input': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Input']
      )[]
    }
    /** Line[Union[Text, Whitespace, Arrow, PassiveSequence]] */
    'Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Output': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Output']
      )[]
    }
    /** MistralAiModel */
    MistralAiModel: {
      /**
       * Provider
       * @default mistralai
       * @constant
       */
      provider: 'mistralai'
      /**
       * Name
       * @enum {string}
       */
      name: 'mistral-large-2411' | 'mistral-small-2501'
    }
    /** MultipleChoicesInput */
    'MultipleChoicesInput-Input': {
      /**
       * Kind
       * @constant
       */
      kind: 'multipleChoicesInput'
      /** Choices */
      choices: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Input'][]
      /** Showchoicesbydefault */
      showChoicesByDefault: boolean
    }
    /** MultipleChoicesInput */
    'MultipleChoicesInput-Output': {
      /**
       * Kind
       * @constant
       */
      kind: 'multipleChoicesInput'
      /** Choices */
      choices: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Output'][]
      /** Showchoicesbydefault */
      showChoicesByDefault: boolean
    }
    /** OpenAiModel */
    OpenAiModel: {
      /**
       * Provider
       * @default openai
       * @constant
       */
      provider: 'openai'
      /**
       * Name
       * @enum {string}
       */
      name: 'gpt-4o-2024-08-06' | 'gpt-4o-mini-2024-07-18'
    }
    /** Page[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input'][]
    }
    /** Page[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output'][]
    }
    /** Page[Union[Text, Whitespace, Arrow, PassiveSequence]] */
    'Page_Union_Text__Whitespace__Arrow__PassiveSequence__-Input': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Input'][]
    }
    /** Page[Union[Text, Whitespace, Arrow, PassiveSequence]] */
    'Page_Union_Text__Whitespace__Arrow__PassiveSequence__-Output': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__PassiveSequence__-Output'][]
    }
    /** Pages[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input': {
      /** Pages */
      pages: components['schemas']['Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Input'][]
    }
    /** Pages[Union[Text, Whitespace, Arrow, FreeTextInput, MultipleChoicesInput, SelectableInput, AnySequence]] */
    'Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output': {
      /** Pages */
      pages: components['schemas']['Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__AnySequence__-Output'][]
    }
    /** PassiveSequence */
    'PassiveSequence-Input': {
      /**
       * Kind
       * @constant
       */
      kind: 'sequence'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Input']
      )[]
      /** Bold */
      bold: boolean
      /** Italic */
      italic: boolean
      /** Highlighted */
      highlighted: string | null
      /** Boxed */
      boxed: boolean
      /** Vertical */
      vertical: boolean
    }
    /** PassiveSequence */
    'PassiveSequence-Output': {
      /**
       * Kind
       * @constant
       */
      kind: 'sequence'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Output']
      )[]
      /** Bold */
      bold: boolean
      /** Italic */
      italic: boolean
      /** Highlighted */
      highlighted: string | null
      /** Boxed */
      boxed: boolean
      /** Vertical */
      vertical: boolean
    }
    /** PostAdaptationAdjustmentRequest */
    PostAdaptationAdjustmentRequest: {
      /** Adjustment */
      adjustment: string
    }
    /** PostAdaptationRequest */
    PostAdaptationRequest: {
      strategy: components['schemas']['Strategy']
      input: components['schemas']['Input']
    }
    /** ProseAndExercise */
    ProseAndExercise: {
      /** Prose */
      prose: string
      structured: components['schemas']['Exercise-Output']
    }
    /** SelectableInput */
    'SelectableInput-Input': {
      /**
       * Kind
       * @constant
       */
      kind: 'selectableInput'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Input']
      )[]
      /** Colors */
      colors: string[]
      /** Boxed */
      boxed: boolean
    }
    /** SelectableInput */
    'SelectableInput-Output': {
      /**
       * Kind
       * @constant
       */
      kind: 'selectableInput'
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['PassiveSequence-Output']
      )[]
      /** Colors */
      colors: string[]
      /** Boxed */
      boxed: boolean
    }
    /** Strategy */
    Strategy: {
      /** Id */
      id: number
      /** Model */
      model:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** Systemprompt */
      systemPrompt: string
    }
    /** SystemMessage */
    SystemMessage: {
      /**
       * Role
       * @default system
       * @constant
       */
      role: 'system'
      /** Message */
      message: string
    }
    /** Text */
    Text: {
      /**
       * Kind
       * @constant
       */
      kind: 'text'
      /** Text */
      text: string
    }
    /** UserMessage */
    UserMessage: {
      /**
       * Role
       * @default user
       * @constant
       */
      role: 'user'
      /** Message */
      message: string
    }
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[]
      /** Message */
      msg: string
      /** Error Type */
      type: string
    }
    /** Whitespace */
    Whitespace: {
      /**
       * Kind
       * @constant
       */
      kind: 'whitespace'
    }
  }
  responses: never
  parameters: never
  requestBodies: never
  headers: never
  pathItems: never
}
export type $defs = Record<string, never>
export interface operations {
  get_available_llm_models_api_available_llm_models_get: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': (
            | components['schemas']['DummyModel']
            | components['schemas']['MistralAiModel']
            | components['schemas']['OpenAiModel']
          )[]
        }
      }
    }
  }
  get_latest_strategy_api_adaptation_latest_strategy_get: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Strategy']
        }
      }
    }
  }
  get_latest_input_api_adaptation_latest_input_get: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Input']
        }
      }
    }
  }
  post_adaptation_api_adaptation_post: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        'application/json': components['schemas']['PostAdaptationRequest']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
  get_adaptation_api_adaptation__id__get: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
  post_adaptation_adjustment_api_adaptation__id__adjustment_post: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody: {
      content: {
        'application/json': components['schemas']['PostAdaptationAdjustmentRequest']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
  delete_adaptation_last_step_api_adaptation__id__last_step_delete: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
  put_adaptation_manual_edit_api_adaptation__id__manual_edit_put: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody: {
      content: {
        'application/json': components['schemas']['Exercise-Input']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
  delete_adaptation_manual_edit_api_adaptation__id__manual_edit_delete: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Adaptation']
        }
      }
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['HTTPValidationError']
        }
      }
    }
  }
}
