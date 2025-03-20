import { mount } from 'cypress/vue'
import compareSnapshotCommand from 'cypress-image-diff-js/command'

import 'modern-normalize/modern-normalize.css'

import '../../src/main.css'

Cypress.Commands.add('mount', mount)
compareSnapshotCommand()
