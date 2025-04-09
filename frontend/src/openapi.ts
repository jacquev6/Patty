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
  '/api/adaptation/llm-response-schema': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /** Get Llm Response Schema */
    post: operations['get_llm_response_schema_api_adaptation_llm_response_schema_post']
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
  '/api/adaptation/export/{id}.html': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Export Adaptation */
    get: operations['export_adaptation_api_adaptation_export__id__html_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
}
export type webhooks = Record<string, never>
export interface components {
  schemas: {
    /** Adjustment */
    Adjustment: {
      /** Userprompt */
      userPrompt: string
      /** Assistanterror */
      assistantError: string | null
      assistantResponse: components['schemas']['Exercise-Output'] | null
    }
    /** ApiAdaptation */
    ApiAdaptation: {
      /** Id */
      id: number
      strategy: components['schemas']['ApiStrategy-Output']
      input: components['schemas']['ApiInput']
      /** Rawllmconversations */
      rawLlmConversations: unknown[]
      /** Initialassistanterror */
      initialAssistantError: string | null
      initialAssistantResponse: components['schemas']['Exercise-Output'] | null
      /** Adjustments */
      adjustments: components['schemas']['Adjustment'][]
      manualEdit: components['schemas']['Exercise-Output'] | null
    }
    /** ApiInput */
    ApiInput: {
      /** Id */
      id: number
      /** Text */
      text: string
    }
    /** ApiStrategy */
    'ApiStrategy-Input': {
      /** Id */
      id: number
      /** Model */
      model:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** Systemprompt */
      systemPrompt: string
      /** Responsespecification */
      responseSpecification:
        | components['schemas']['JsonFromTextLlmResponseSpecification']
        | components['schemas']['JsonObjectLlmResponseSpecification']
        | components['schemas']['JsonSchemaLlmResponseSpecification']
    }
    /** ApiStrategy */
    'ApiStrategy-Output': {
      /** Id */
      id: number
      /** Model */
      model:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** Systemprompt */
      systemPrompt: string
      /** Responsespecification */
      responseSpecification:
        | components['schemas']['JsonFromTextLlmResponseSpecification']
        | components['schemas']['JsonObjectLlmResponseSpecification']
        | components['schemas']['JsonSchemaLlmResponseSpecification']
    }
    Arrow: {
      /**
       * Kind
       * @constant
       */
      kind: 'arrow'
    }
    Choice: {
      /**
       * Kind
       * @constant
       */
      kind: 'choice'
      /** Contents */
      contents: (components['schemas']['Text'] | components['schemas']['Whitespace'])[]
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
    'Exercise-Input': {
      /**
       * Format
       * @constant
       */
      format: 'v1'
      instruction: components['schemas']['Page_Union_Text__Whitespace__Choice__-Input']
      statement: components['schemas']['Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input']
      reference: components['schemas']['Line_Union_Text__Whitespace__'] | null
    }
    'Exercise-Output': {
      /**
       * Format
       * @constant
       */
      format: 'v1'
      instruction: components['schemas']['Page_Union_Text__Whitespace__Choice__-Output']
      statement: components['schemas']['Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output']
      reference: components['schemas']['Line_Union_Text__Whitespace__'] | null
    }
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
    /** InstructionComponents */
    InstructionComponents: {
      /**
       * Text
       * @constant
       */
      text: true
      /**
       * Whitespace
       * @constant
       */
      whitespace: true
      /** Choice */
      choice: boolean
    }
    /** JsonFromTextLlmResponseSpecification */
    JsonFromTextLlmResponseSpecification: {
      /**
       * Format
       * @constant
       */
      format: 'json'
      /**
       * Formalism
       * @constant
       */
      formalism: 'text'
    }
    /** JsonObjectLlmResponseSpecification */
    JsonObjectLlmResponseSpecification: {
      /**
       * Format
       * @constant
       */
      format: 'json'
      /**
       * Formalism
       * @constant
       */
      formalism: 'json-object'
    }
    /** JsonSchemaLlmResponseSpecification */
    JsonSchemaLlmResponseSpecification: {
      /**
       * Format
       * @constant
       */
      format: 'json'
      /**
       * Formalism
       * @constant
       */
      formalism: 'json-schema'
      instructionComponents: components['schemas']['InstructionComponents']
      statementComponents: components['schemas']['StatementComponents']
      referenceComponents: components['schemas']['ReferenceComponents']
    }
    Line_Union_Text__Whitespace__: {
      /** Contents */
      contents: (components['schemas']['Text'] | components['schemas']['Whitespace'])[]
    }
    'Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Input']
        | components['schemas']['SelectableInput']
      )[]
    }
    'Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Arrow']
        | components['schemas']['FreeTextInput']
        | components['schemas']['MultipleChoicesInput-Output']
        | components['schemas']['SelectableInput']
      )[]
    }
    'Line_Union_Text__Whitespace__Choice__-Input': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Choice']
      )[]
    }
    'Line_Union_Text__Whitespace__Choice__-Output': {
      /** Contents */
      contents: (
        | components['schemas']['Text']
        | components['schemas']['Whitespace']
        | components['schemas']['Choice']
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
    'MultipleChoicesInput-Input': {
      /**
       * Kind
       * @constant
       */
      kind: 'multipleChoicesInput'
      /** Choices */
      choices: components['schemas']['PureTextContainer'][]
      /** Showchoicesbydefault */
      showChoicesByDefault: boolean
    }
    'MultipleChoicesInput-Output': {
      /**
       * Kind
       * @constant
       */
      kind: 'multipleChoicesInput'
      /** Choices */
      choices: components['schemas']['PureTextContainer'][]
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
    'Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input'][]
    }
    'Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output'][]
    }
    'Page_Union_Text__Whitespace__Choice__-Input': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Choice__-Input'][]
    }
    'Page_Union_Text__Whitespace__Choice__-Output': {
      /** Lines */
      lines: components['schemas']['Line_Union_Text__Whitespace__Choice__-Output'][]
    }
    'Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input': {
      /** Pages */
      pages: components['schemas']['Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Input'][]
    }
    'Pages_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output': {
      /** Pages */
      pages: components['schemas']['Page_Union_Text__Whitespace__Arrow__FreeTextInput__MultipleChoicesInput__SelectableInput__-Output'][]
    }
    /** PostAdaptationAdjustmentRequest */
    PostAdaptationAdjustmentRequest: {
      /** Adjustment */
      adjustment: string
    }
    /** PostAdaptationRequest */
    PostAdaptationRequest: {
      strategy: components['schemas']['ApiStrategy-Input']
      input: components['schemas']['ApiInput']
    }
    PureTextContainer: {
      /** Contents */
      contents: (components['schemas']['Text'] | components['schemas']['Whitespace'])[]
    }
    /** ReferenceComponents */
    ReferenceComponents: {
      /**
       * Text
       * @constant
       */
      text: true
      /**
       * Whitespace
       * @constant
       */
      whitespace: true
    }
    SelectableInput: {
      /**
       * Kind
       * @constant
       */
      kind: 'selectableInput'
      /** Contents */
      contents: (components['schemas']['Text'] | components['schemas']['Whitespace'])[]
      /** Colors */
      colors: string[]
      /** Boxed */
      boxed: boolean
    }
    /** StatementComponents */
    StatementComponents: {
      /**
       * Text
       * @constant
       */
      text: true
      /**
       * Whitespace
       * @constant
       */
      whitespace: true
      /** Arrow */
      arrow: boolean
      /** Freetextinput */
      freeTextInput: boolean
      /** Multiplechoicesinput */
      multipleChoicesInput: boolean
      /** Selectableinput */
      selectableInput: boolean
    }
    Text: {
      /**
       * Kind
       * @constant
       */
      kind: 'text'
      /** Text */
      text: string
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
          'application/json': components['schemas']['ApiStrategy-Output']
        }
      }
    }
  }
  get_llm_response_schema_api_adaptation_llm_response_schema_post: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        'application/json': components['schemas']['JsonSchemaLlmResponseSpecification']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': Record<string, never>
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
          'application/json': components['schemas']['ApiInput']
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
          'application/json': components['schemas']['ApiAdaptation']
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
          'application/json': components['schemas']['ApiAdaptation']
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
          'application/json': components['schemas']['ApiAdaptation']
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
          'application/json': components['schemas']['ApiAdaptation']
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
          'application/json': components['schemas']['ApiAdaptation']
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
          'application/json': components['schemas']['ApiAdaptation']
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
  export_adaptation_api_adaptation_export__id__html_get: {
    parameters: {
      query?: {
        download?: boolean
      }
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
          'text/html': string
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
