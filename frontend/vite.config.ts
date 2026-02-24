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

import { fileURLToPath, URL } from 'node:url'
import { promises as fs } from 'fs'
import path, { dirname } from 'node:path'

import { defineConfig, Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { viteSingleFile } from 'vite-plugin-singlefile'
import vueI18n from '@intlify/unplugin-vue-i18n/vite'


// @todo Maybe this whacky plugin could be replaced using the 'build.rollupOptions.input' option of Vite?
function readOtherIndexHtml(name : string) : Plugin {
  // Warning: this hack breaks the '--watch' option of 'vite build' for the '${name}.html' file (because it still thinks it's reading 'index.html').
  // Accepted for now.
  return {
    name: 'vite-plugin-read-other-index-html',
    transformIndexHtml: {
      order: 'pre',
      async handler() {
        return await fs.readFile(`src/${name}/index.html`, 'utf8')
      },
    },
  }
}

export default defineConfig(({ command/*, mode, isSsrBuild, isPreview*/ }) => {
  const entryPointName = process.env.PATTY_ENTRY_POINT_NAME as string

  const plugins: (Plugin | ReturnType<typeof vueDevTools>)[] = [
    readOtherIndexHtml(entryPointName),
    vue(),
    vueI18n({
      include: path.resolve(dirname(fileURLToPath(import.meta.url)), './src/frontend/locales/**'),
      defaultSFCLang: 'yml',
      strictMessage: false,
    })
  ]
  
  // @todo Find a way to re-enable Vue DevTools for interactive development but not for end-to-end testing: they pollute visual tests.
  // plugins.push(vueDevTools())
  // When Vue DevTools are enabled, you can run the following in a shell to enable opening VSCode from the browser:
  //   ./dev.sh compose -- logs --since 0m --follow frontend | stdbuf -oL sed 's/^.*| //' | stdbuf -oL grep '^code' | sh

  if (command === 'build' && entryPointName !== 'frontend') {
    // Generate a standalone HTML file that can be downloaded and opened offline
    // (actually used as a template in the FastAPI app first)
    plugins.push(viteSingleFile() as Plugin)
  }

  return {
    publicDir: `src/${entryPointName}/public`,
    plugins,
    server: {
      allowedHosts: true,
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '$': fileURLToPath(new URL('./src/reusable', import.meta.url)),
      },
    },
  }
})
