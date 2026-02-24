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

export function ignoreResizeObserverLoopError() {
  Cypress.on('uncaught:exception', (error) => {
    if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
      // @todo Deep dive into this issue: avoid the error instead of ignoring it.
      // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
      return false
    } else {
      return true
    }
  })
}

export function screenshot(name: string) {
  if (!Cypress.config('isInteractive')) {
    cy.compareSnapshot({
      name,
      cypressScreenshotOptions: { disableTimersAndAnimations: true },
    })
  }
}

export function visit(url: string) {
  cy.visit(url)
  cy.get('[data-cy="password"]').type('password')
  cy.get('[data-cy="submit"]').click()
  cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
  cy.get('[data-cy="identified-user-ok"]').click()
}

export function loadFixtures(fixtures_: string[]) {
  const fixtures = fixtures_.join(',')
  cy.request('POST', `http://fixtures-loader/load?fixtures=${fixtures}`)
}

export function visitExport(url: string) {
  cy.request('POST', '/api/token', { password: 'password' }).then((response) => {
    cy.visit(`${url}?download=false&token=${response.body.accessToken}`)
  })
}
