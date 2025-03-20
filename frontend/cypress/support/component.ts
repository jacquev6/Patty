import { mount } from 'cypress/vue'
import 'modern-normalize/modern-normalize.css'

import '../../src/main.css'

Cypress.Commands.add('mount', mount)
