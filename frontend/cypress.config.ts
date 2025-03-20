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
      return getCompareSnapshotsPlugin(on, config)
    },
  },
})
