import { mount } from 'cypress/vue'
import compareSnapshotCommand from 'cypress-image-diff-js/command'

import 'modern-normalize/modern-normalize.css'

import '../../src/frontend/main.css'

Cypress.Commands.add('mount', mount)
// https://github.com/cypress-io/cypress/issues/17712#issuecomment-1646614336
Cypress.Commands.add('vue', () => cy.wrap(Cypress.vueWrapper))
compareSnapshotCommand()
