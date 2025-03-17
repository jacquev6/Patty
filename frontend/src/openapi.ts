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
  '/api/tokenization/default-system-prompt': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Default Tokenization System Prompt */
    get: operations['get_default_tokenization_system_prompt_api_tokenization_default_system_prompt_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/tokenization': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /** Post Tokenization */
    post: operations['post_tokenization_api_tokenization_post']
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/tokenization/{id}': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Tokenization */
    get: operations['get_tokenization_api_tokenization__id__get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/tokenization/{id}/adjustment': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /** Post Tokenization Adjustment */
    post: operations['post_tokenization_adjustment_api_tokenization__id__adjustment_post']
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/tokenization/{id}/last-step': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post?: never
    /** Delete Tokenization Last Step */
    delete: operations['delete_tokenization_last_step_api_tokenization__id__last_step_delete']
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
}
export type webhooks = Record<string, never>
export interface components {
  schemas: {
    /** AdjustmentStep */
    AdjustmentStep: {
      /**
       * Kind
       * @constant
       */
      kind: 'adjustment'
      /** User Prompt */
      user_prompt: string
      /** Messages */
      messages: (
        | components['schemas']['UserMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['AssistantMessage_TokenizedText_']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
    }
    /** AssistantMessage[TokenizedText] */
    AssistantMessage_TokenizedText_: {
      /**
       * Role
       * @default assistant
       * @constant
       */
      role: 'assistant'
      /** Prose */
      prose: string
      structured: components['schemas']['TokenizedText'] | null
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
      /** System Prompt */
      system_prompt: string
      /** Input Text */
      input_text: string
      /** Messages */
      messages: (
        | components['schemas']['UserMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['AssistantMessage_TokenizedText_']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
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
    /** PostTokenizationAdjustmentRequest */
    PostTokenizationAdjustmentRequest: {
      /** Adjustment */
      adjustment: string
    }
    /** PostTokenizationRequest */
    PostTokenizationRequest: {
      /** Llm Model */
      llm_model:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** System Prompt */
      system_prompt: string
      /** Input Text */
      input_text: string
    }
    /** Punctuation */
    Punctuation: {
      /**
       * Kind
       * @constant
       */
      kind: 'punctuation'
      /** Text */
      text: string
    }
    /** Sentence */
    Sentence: {
      /** Tokens */
      tokens: (components['schemas']['Word'] | components['schemas']['Punctuation'])[]
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
    /** Tokenization */
    Tokenization: {
      /** Id */
      id: string
      /** Llm Model */
      llm_model:
        | components['schemas']['DummyModel']
        | components['schemas']['MistralAiModel']
        | components['schemas']['OpenAiModel']
      /** Steps */
      steps: (components['schemas']['InitialStep'] | components['schemas']['AdjustmentStep'])[]
    }
    /** TokenizedText */
    TokenizedText: {
      /** Sentences */
      sentences: components['schemas']['Sentence'][]
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
    /** Word */
    Word: {
      /**
       * Kind
       * @constant
       */
      kind: 'word'
      /** Text */
      text: string
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
  get_default_tokenization_system_prompt_api_tokenization_default_system_prompt_get: {
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
          'application/json': string
        }
      }
    }
  }
  post_tokenization_api_tokenization_post: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        'application/json': components['schemas']['PostTokenizationRequest']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Tokenization']
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
  get_tokenization_api_tokenization__id__get: {
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
          'application/json': components['schemas']['Tokenization']
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
  post_tokenization_adjustment_api_tokenization__id__adjustment_post: {
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
        'application/json': components['schemas']['PostTokenizationAdjustmentRequest']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['Tokenization']
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
  delete_tokenization_last_step_api_tokenization__id__last_step_delete: {
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
          'application/json': components['schemas']['Tokenization']
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
