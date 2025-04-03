import { defineConfig } from 'cypress'
import getCompareSnapshotsPlugin from 'cypress-image-diff-js/plugin'


function setupNodeEvents(on: Cypress.PluginEvents, config: Cypress.PluginConfigOptions) {
  config = getCompareSnapshotsPlugin(on, config)

  // Inspired by the contents of 'getCompareSnapshotsPlugin' but fixed for browser.name === 'chromium'
  on('before:browser:launch', function (browser, launchOptions) {
    const width = 1600
    const height = 1200

    if (browser.name === 'chromium') {
      launchOptions.args.push(`--window-size=${width},${height}`)
      launchOptions.args.push('--force-device-scale-factor=1')
    }

    if (browser.name === 'electron') {
      launchOptions.preferences.width = width
      launchOptions.preferences.height = height
    }

    if (browser.name === 'firefox') {
      launchOptions.args.push(`--width=${width}`)
      launchOptions.args.push(`--height=${height}`)
    }

    return launchOptions
  })

  return config
}


export default defineConfig({
  component: {
    specPattern: 'src/**/*.cy.ts',
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    setupNodeEvents,
  },

  e2e: {
    baseUrl: 'http://fanout:8080/',
    specPattern: 'e2e-tests/**/*.cy.ts',  // @todo Move to ../e2e-tests
    setupNodeEvents,
  },
})
