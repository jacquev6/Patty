import TextArea from './TextArea.vue'

describe('TextArea', () => {
  before(console.clear)

  it('gets its size from its initial model', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea, { props: { modelValue: 'Blah\nBlah\nBlah\n' } })
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'
    cy.get('textarea').should('have.css', 'height', large)
  })

  it('resizes with content when typing', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea)

    const small = { firefox: '45px' }[Cypress.browser.name] ?? '43px'
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'

    cy.get('textarea').should('have.css', 'height', small)
    cy.get('textarea').type('Blah\nBlah\nBlah\n', { delay: 0 })
    cy.get('textarea').should('have.css', 'height', large)
    cy.get('textarea').type('{selectall}{backspace}', { delay: 0 })
    cy.get('textarea').should('have.css', 'height', small)
  })

  it('resizes with window width', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea)

    cy.get('textarea').type(
      'Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah',
      { delay: 0 },
    )

    const small = { firefox: '64px' }[Cypress.browser.name] ?? '61px'
    const large = { firefox: '100px' }[Cypress.browser.name] ?? '98px'

    cy.get('textarea').should('have.css', 'height', small)
    cy.viewport(300, 500)
    cy.get('textarea').should('have.css', 'height', large)
    cy.viewport(500, 500)
    cy.get('textarea').should('have.css', 'height', small)
  })

  it('resizes when model is changed', () => {
    cy.viewport(500, 500)

    const small = { firefox: '45px' }[Cypress.browser.name] ?? '43px'
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'

    cy.mount(TextArea, { props: { modelValue: '' } })
    cy.get('textarea').should('have.value', '')
    cy.get('textarea').should('have.css', 'height', small)
    cy.vue<typeof TextArea>().then((wrapper) => wrapper.setProps({ modelValue: 'Blah\nBlah\nBlah\n' }))
    cy.get('textarea').should('have.value', 'Blah\nBlah\nBlah\n')
    cy.get('textarea').should('have.css', 'height', large)
    cy.vue<typeof TextArea>().then((wrapper) => wrapper.setProps({ modelValue: '' }))
    cy.get('textarea').should('have.value', '')
    cy.get('textarea').should('have.css', 'height', small)
  })
})
