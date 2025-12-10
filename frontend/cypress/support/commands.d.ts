// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import { mount } from 'cypress/vue'

declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
      vue<C>(): Chainable<VueWrapper<C>>
    }
  }
}
