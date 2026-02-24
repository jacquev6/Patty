<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import VirtualKeyboardButton from './VirtualKeyboardButton.vue'

function click() {
  const el = document.activeElement
  if (el instanceof HTMLElement && el.getAttribute('contenteditable') !== null) {
    el.textContent = ''
    el.dispatchEvent(new InputEvent('input', { inputType: '' }))
  } else {
    console.log('Active element not handled:', el)
  }
}
</script>

<template>
  <!-- VirtualEraser.png has been provided by the client in https://github.com/jacquev6/Patty/issues/91 -->
  <VirtualKeyboardButton @click="click"><img height="32" src="./VirtualEraser.png" /></VirtualKeyboardButton>
</template>

<style scoped>
img {
  vertical-align: text-bottom;
}
</style>
