import { rmdir } from 'fs'
import { defineConfig } from 'cypress'
import getCompareSnapshotsPlugin from 'cypress-image-diff-js/plugin'


function setupNodeEvents(on: Cypress.PluginEvents, config: Cypress.PluginConfigOptions) {
  config = getCompareSnapshotsPlugin(on, config)

  // Enable high-resolution screenshots (inspired by the contents of 'getCompareSnapshotsPlugin' but fixed for browser.name === 'chromium')
  // Disable spellcheck
  on('before:browser:launch', function (browser, launchOptions) {
    const width = 2000
    const height = 1200

    if (browser.name === 'chromium') {
      launchOptions.args.push(`--window-size=${width},${height}`)
      launchOptions.args.push('--force-device-scale-factor=1')
      launchOptions.preferences.default['browser.enable_spellchecking'] = false
    }

    if (browser.name === 'electron') {
      launchOptions.preferences.width = width
      launchOptions.preferences.height = height
      launchOptions.preferences.webPreferences.spellcheck = false
    }

    if (browser.name === 'firefox') {
      launchOptions.args.push(`--width=${width}`)
      launchOptions.args.push(`--height=${height}`)
      launchOptions.preferences['layout.spellcheckDefault'] = 0
    }

    return launchOptions
  })

  on('task', {
    deleteFolder(folderName) {
      return new Promise((resolve) => {
        rmdir(folderName, { recursive: true }, () => resolve(null))
      })
    },
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
    specPattern: 'e2e-tests/**/*.cy.ts',
    setupNodeEvents,
  },
})
