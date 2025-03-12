/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */

export interface paths {
  '/api/get-cheese': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Cheese */
    get: operations['get_cheese_api_get_cheese_get']
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  '/api/default-tokenization-system-prompt': {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /** Get Default Tokenization System Prompt */
    get: operations['get_default_tokenization_system_prompt_api_default_tokenization_system_prompt_get']
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
    Arguments: Record<string, never> | string
    /** AssistantMessage */
    AssistantMessage: {
      /** @default ~?~unset~?~sentinel~?~ */
      content: components['schemas']['OptionalNullable_AssistantMessageContent_']
      /** @default ~?~unset~?~sentinel~?~ */
      tool_calls: components['schemas']['OptionalNullable_List_ToolCall__']
      /**
       * Prefix
       * @default false
       */
      prefix: boolean | null
      /**
       * Role
       * @default assistant
       */
      role: 'assistant' | null
    }
    AssistantMessageContent:
      | string
      | (
          | components['schemas']['ImageURLChunk']
          | components['schemas']['DocumentURLChunk']
          | components['schemas']['TextChunk']
          | components['schemas']['ReferenceChunk']
        )[]
    /** Audio */
    Audio: {
      /** Id */
      id: string
    }
    /** ChatCompletionAssistantMessageParam */
    ChatCompletionAssistantMessageParam: {
      /**
       * Role
       * @constant
       */
      role: 'assistant'
      audio?: components['schemas']['Audio'] | null
      /** Content */
      content?:
        | string
        | (
            | components['schemas']['ChatCompletionContentPartTextParam']
            | components['schemas']['ChatCompletionContentPartRefusalParam']
          )[]
        | null
      function_call?:
        | components['schemas']['openai__types__chat__chat_completion_assistant_message_param__FunctionCall']
        | null
      /** Name */
      name?: string
      /** Refusal */
      refusal?: string | null
      /** Tool Calls */
      tool_calls?: components['schemas']['ChatCompletionMessageToolCallParam'][]
    }
    /** ChatCompletionContentPartImageParam */
    ChatCompletionContentPartImageParam: {
      image_url: components['schemas']['openai__types__chat__chat_completion_content_part_image_param__ImageURL']
      /**
       * Type
       * @constant
       */
      type: 'image_url'
    }
    /** ChatCompletionContentPartInputAudioParam */
    ChatCompletionContentPartInputAudioParam: {
      input_audio: components['schemas']['InputAudio']
      /**
       * Type
       * @constant
       */
      type: 'input_audio'
    }
    /** ChatCompletionContentPartRefusalParam */
    ChatCompletionContentPartRefusalParam: {
      /** Refusal */
      refusal: string
      /**
       * Type
       * @constant
       */
      type: 'refusal'
    }
    /** ChatCompletionContentPartTextParam */
    ChatCompletionContentPartTextParam: {
      /** Text */
      text: string
      /**
       * Type
       * @constant
       */
      type: 'text'
    }
    /** ChatCompletionDeveloperMessageParam */
    ChatCompletionDeveloperMessageParam: {
      /** Content */
      content: string | components['schemas']['ChatCompletionContentPartTextParam'][]
      /**
       * Role
       * @constant
       */
      role: 'developer'
      /** Name */
      name?: string
    }
    /** ChatCompletionFunctionMessageParam */
    ChatCompletionFunctionMessageParam: {
      /** Content */
      content: string | null
      /** Name */
      name: string
      /**
       * Role
       * @constant
       */
      role: 'function'
    }
    /** ChatCompletionMessageToolCallParam */
    ChatCompletionMessageToolCallParam: {
      /** Id */
      id: string
      function: components['schemas']['Function']
      /**
       * Type
       * @constant
       */
      type: 'function'
    }
    /** ChatCompletionSystemMessageParam */
    ChatCompletionSystemMessageParam: {
      /** Content */
      content: string | components['schemas']['ChatCompletionContentPartTextParam'][]
      /**
       * Role
       * @constant
       */
      role: 'system'
      /** Name */
      name?: string
    }
    /** ChatCompletionToolMessageParam */
    ChatCompletionToolMessageParam: {
      /** Content */
      content: string | components['schemas']['ChatCompletionContentPartTextParam'][]
      /**
       * Role
       * @constant
       */
      role: 'tool'
      /** Tool Call Id */
      tool_call_id: string
    }
    /** ChatCompletionUserMessageParam */
    ChatCompletionUserMessageParam: {
      /** Content */
      content:
        | string
        | (
            | components['schemas']['ChatCompletionContentPartTextParam']
            | components['schemas']['ChatCompletionContentPartImageParam']
            | components['schemas']['ChatCompletionContentPartInputAudioParam']
            | components['schemas']['File']
          )[]
      /**
       * Role
       * @constant
       */
      role: 'user'
      /** Name */
      name?: string
    }
    /** Cheese */
    Cheese: {
      /** Name */
      name: string
    }
    /** DocumentURLChunk */
    DocumentURLChunk: {
      /** Document Url */
      document_url: string
      /**
       * Type
       * @default document_url
       */
      type: 'document_url' | null
      /** @default ~?~unset~?~sentinel~?~ */
      document_name: components['schemas']['OptionalNullable_str_']
    }
    /** File */
    File: {
      file: components['schemas']['FileFile']
      /**
       * Type
       * @constant
       */
      type: 'file'
    }
    /** FileFile */
    FileFile: {
      /** File Data */
      file_data?: string
      /** File Id */
      file_id?: string
      /** File Name */
      file_name?: string
    }
    /** Function */
    Function: {
      /** Arguments */
      arguments: string
      /** Name */
      name: string
    }
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components['schemas']['ValidationError'][]
    }
    /**
     * ImageURLChunk
     * @description {\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/png;base64,iVBORw0
     */
    ImageURLChunk: {
      image_url: components['schemas']['ImageURLChunkImageURL']
      /**
       * Type
       * @default image_url
       */
      type: 'image_url' | null
    }
    ImageURLChunkImageURL: components['schemas']['mistralai__models__imageurl__ImageURL'] | string
    /** InputAudio */
    InputAudio: {
      /** Data */
      data: string
      /**
       * Format
       * @enum {string}
       */
      format: 'wav' | 'mp3'
    }
    /** MistralAdjustmentStep */
    MistralAdjustmentStep: {
      /**
       * Kind
       * @constant
       */
      kind: 'adjustment'
      /** User Prompt */
      user_prompt: string
      /** Messages */
      messages: (
        | components['schemas']['AssistantMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['ToolMessage']
        | components['schemas']['UserMessage']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
    }
    /** MistralInitialStep */
    MistralInitialStep: {
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
        | components['schemas']['AssistantMessage']
        | components['schemas']['SystemMessage']
        | components['schemas']['ToolMessage']
        | components['schemas']['UserMessage']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
    }
    /** MistralPostTokenizationRequest */
    MistralPostTokenizationRequest: {
      /**
       * Llm Provider
       * @constant
       */
      llm_provider: 'mistralai'
      /**
       * Mistral Model
       * @enum {string}
       */
      mistral_model: 'mistral-large-2411' | 'mistral-small-2501'
      /** System Prompt */
      system_prompt: string
      /** Input Text */
      input_text: string
    }
    /** MistralTokenization */
    MistralTokenization: {
      /** Id */
      id: string
      /**
       * Llm Provider
       * @constant
       */
      llm_provider: 'mistralai'
      /**
       * Mistral Model
       * @enum {string}
       */
      mistral_model: 'mistral-large-2411' | 'mistral-small-2501'
      /** Steps */
      steps: (components['schemas']['MistralInitialStep'] | components['schemas']['MistralAdjustmentStep'])[]
    }
    Nullable_AssistantMessageContent_: components['schemas']['AssistantMessageContent'] | null
    Nullable_List_ToolCall__: components['schemas']['ToolCall'][] | null
    Nullable_ToolMessageContent_: components['schemas']['ToolMessageContent'] | null
    Nullable_UserMessageContent_: components['schemas']['UserMessageContent'] | null
    Nullable_str_: string | null
    /** OpenaiAdjustmentStep */
    OpenaiAdjustmentStep: {
      /**
       * Kind
       * @constant
       */
      kind: 'adjustment'
      /** User Prompt */
      user_prompt: string
      /** Messages */
      messages: (
        | components['schemas']['ChatCompletionDeveloperMessageParam']
        | components['schemas']['ChatCompletionSystemMessageParam']
        | components['schemas']['ChatCompletionUserMessageParam']
        | components['schemas']['ChatCompletionAssistantMessageParam']
        | components['schemas']['ChatCompletionToolMessageParam']
        | components['schemas']['ChatCompletionFunctionMessageParam']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
    }
    /** OpenaiInitialStep */
    OpenaiInitialStep: {
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
        | components['schemas']['ChatCompletionDeveloperMessageParam']
        | components['schemas']['ChatCompletionSystemMessageParam']
        | components['schemas']['ChatCompletionUserMessageParam']
        | components['schemas']['ChatCompletionAssistantMessageParam']
        | components['schemas']['ChatCompletionToolMessageParam']
        | components['schemas']['ChatCompletionFunctionMessageParam']
      )[]
      /** Assistant Prose */
      assistant_prose: string
      tokenized_text: components['schemas']['TokenizedText'] | null
    }
    /** OpenaiPostTokenizationRequest */
    OpenaiPostTokenizationRequest: {
      /**
       * Llm Provider
       * @constant
       */
      llm_provider: 'openai'
      /**
       * Openai Model
       * @enum {string}
       */
      openai_model: 'gpt-4o-2024-08-06' | 'gpt-4o-mini-2024-07-18'
      /** System Prompt */
      system_prompt: string
      /** Input Text */
      input_text: string
    }
    /** OpenaiTokenization */
    OpenaiTokenization: {
      /** Id */
      id: string
      /**
       * Llm Provider
       * @constant
       */
      llm_provider: 'openai'
      /**
       * Openai Model
       * @enum {string}
       */
      openai_model: 'gpt-4o-2024-08-06' | 'gpt-4o-mini-2024-07-18'
      /** Steps */
      steps: (components['schemas']['OpenaiInitialStep'] | components['schemas']['OpenaiAdjustmentStep'])[]
    }
    OptionalNullable_AssistantMessageContent_:
      | components['schemas']['Nullable_AssistantMessageContent_']
      | components['schemas']['Unset']
      | null
    OptionalNullable_List_ToolCall__:
      | components['schemas']['Nullable_List_ToolCall__']
      | components['schemas']['Unset']
      | null
    OptionalNullable_str_: components['schemas']['Nullable_str_'] | components['schemas']['Unset'] | null
    /** PostTokenizationAdjustmentRequest */
    PostTokenizationAdjustmentRequest: {
      /** Adjustment */
      adjustment: string
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
    /** ReferenceChunk */
    ReferenceChunk: {
      /** Reference Ids */
      reference_ids: number[]
      /**
       * Type
       * @default reference
       */
      type: 'reference' | null
    }
    /** Sentence */
    Sentence: {
      /** Tokens */
      tokens: (components['schemas']['Word'] | components['schemas']['Punctuation'])[]
    }
    /** SystemMessage */
    SystemMessage: {
      content: components['schemas']['SystemMessageContent']
      /**
       * Role
       * @default system
       */
      role: 'system' | null
    }
    SystemMessageContent: string | components['schemas']['TextChunk'][]
    /** TextChunk */
    TextChunk: {
      /** Text */
      text: string
      /**
       * Type
       * @default text
       */
      type: 'text' | null
    }
    /** TokenizedText */
    TokenizedText: {
      /** Sentences */
      sentences: components['schemas']['Sentence'][]
    }
    /** ToolCall */
    ToolCall: {
      function: components['schemas']['mistralai__models__functioncall__FunctionCall']
      /**
       * Id
       * @default null
       */
      id: string | null
      /** Type */
      type?: 'function' | string | null
      /**
       * Index
       * @default 0
       */
      index: number | null
    }
    /** ToolMessage */
    ToolMessage: {
      content: components['schemas']['Nullable_ToolMessageContent_']
      /** @default ~?~unset~?~sentinel~?~ */
      tool_call_id: components['schemas']['OptionalNullable_str_']
      /** @default ~?~unset~?~sentinel~?~ */
      name: components['schemas']['OptionalNullable_str_']
      /**
       * Role
       * @default tool
       */
      role: 'tool' | null
    }
    ToolMessageContent:
      | string
      | (
          | components['schemas']['ImageURLChunk']
          | components['schemas']['DocumentURLChunk']
          | components['schemas']['TextChunk']
          | components['schemas']['ReferenceChunk']
        )[]
    /** Unset */
    Unset: Record<string, never>
    /** UserMessage */
    UserMessage: {
      content: components['schemas']['Nullable_UserMessageContent_']
      /**
       * Role
       * @default user
       */
      role: 'user' | null
    }
    UserMessageContent:
      | string
      | (
          | components['schemas']['ImageURLChunk']
          | components['schemas']['DocumentURLChunk']
          | components['schemas']['TextChunk']
          | components['schemas']['ReferenceChunk']
        )[]
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
    /** FunctionCall */
    mistralai__models__functioncall__FunctionCall: {
      /** Name */
      name: string
      arguments: components['schemas']['Arguments']
    }
    /** ImageURL */
    mistralai__models__imageurl__ImageURL: {
      /** Url */
      url: string
      /** @default ~?~unset~?~sentinel~?~ */
      detail: components['schemas']['OptionalNullable_str_']
    }
    /** FunctionCall */
    openai__types__chat__chat_completion_assistant_message_param__FunctionCall: {
      /** Arguments */
      arguments: string
      /** Name */
      name: string
    }
    /** ImageURL */
    openai__types__chat__chat_completion_content_part_image_param__ImageURL: {
      /** Url */
      url: string
      /**
       * Detail
       * @enum {string}
       */
      detail?: 'auto' | 'low' | 'high'
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
  get_cheese_api_get_cheese_get: {
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
          'application/json': components['schemas']['Cheese']
        }
      }
    }
  }
  get_default_tokenization_system_prompt_api_default_tokenization_system_prompt_get: {
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
        'application/json':
          | components['schemas']['MistralPostTokenizationRequest']
          | components['schemas']['OpenaiPostTokenizationRequest']
      }
    }
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          'application/json': components['schemas']['MistralTokenization'] | components['schemas']['OpenaiTokenization']
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
          'application/json': components['schemas']['MistralTokenization'] | components['schemas']['OpenaiTokenization']
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
          'application/json': components['schemas']['MistralTokenization'] | components['schemas']['OpenaiTokenization']
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
          'application/json': components['schemas']['MistralTokenization'] | components['schemas']['OpenaiTokenization']
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
