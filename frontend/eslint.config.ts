import pluginVue from 'eslint-plugin-vue'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
// @ts-expect-error Not typed
import pluginCypress from 'eslint-plugin-cypress/flat'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import vueI18n from '@intlify/eslint-plugin-vue-i18n'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },

  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  {
    ...pluginCypress.configs.recommended,
    files: [
      '**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}',
      'cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}',
      'cypress/support/**/*.{js,ts,jsx,tsx}'
    ],
  },
  skipFormatting,
  vueI18n.configs.recommended,
  {
    rules: {
      'vue/require-v-for-key': 'off',
      'vue/valid-v-for': 'off',
      '@intlify/vue-i18n/no-raw-text': [
        'error',
        // Use the following comment to ignore this rule on a specific line:
        // <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        {
          ignoreText: [
            ',', ':', '.', '(', ')', '/', '<', '>', '✅', '❌', '🌐', '🖊️', '👤', 'BUG:',
          ],
        },
      ],
      // @todo Find how to disable these '@intlify' rules only for .json files
      '@intlify/vue-i18n/no-deprecated-modulo-syntax': 'off',
      '@intlify/vue-i18n/no-html-messages': 'off',
      '@intlify/vue-i18n/valid-message-syntax': 'off',
    },
  },
)
