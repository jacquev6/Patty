// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import { mount } from 'cypress/vue'
import compareSnapshotCommand from 'cypress-image-diff-js/command'

import 'modern-normalize/modern-normalize.css'

import '../../src/frontend/main.css'

Cypress.Commands.add('mount', mount)
// https://github.com/cypress-io/cypress/issues/17712#issuecomment-1646614336
Cypress.Commands.add('vue', () => cy.wrap(Cypress.vueWrapper))
compareSnapshotCommand()
