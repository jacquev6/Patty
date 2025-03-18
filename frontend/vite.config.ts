import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'


const plugins: (ReturnType<typeof vue> | ReturnType<typeof vueDevTools>)[] = [
  vue({
    template: {
      compilerOptions: {
        whitespace: 'preserve'
      }
    }
  }),
]

if (process.env.PATTY_UNIT_TESTING !== 'true') {
  plugins.push(vueDevTools())
}

// https://vite.dev/config/
export default defineConfig({
  plugins,
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
