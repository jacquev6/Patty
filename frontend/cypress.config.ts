import { defineConfig } from 'cypress'
import getCompareSnapshotsPlugin from 'cypress-image-diff-js/plugin'

export default defineConfig({
  component: {
    specPattern: 'src/**/*.cy.ts',
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    setupNodeEvents(on, config) {
      // Used by 'getCompareSnapshotsPlugin' below to set the window size, hence the max screenshot size
      config.viewportWidth = 1600
      config.viewportHeight = 1200
      return getCompareSnapshotsPlugin(on, config)
    },
  },

  e2e: {
    baseUrl: 'http://fanout:8080/',
    specPattern: 'e2e-tests/**/*.cy.ts',  // @todo Move to ../e2e-tests
    setupNodeEvents(on, config) {
      return getCompareSnapshotsPlugin(on, config)
    },
  },
})
