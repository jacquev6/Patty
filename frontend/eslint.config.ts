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
            ',', ':', '.', '(', ')', '/', '<', '>', '-', '✅', '❌', '🌐', '🖊️', '👤', 'BUG:',
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
