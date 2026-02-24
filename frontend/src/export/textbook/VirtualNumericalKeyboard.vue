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
import assert from '$/assert'
import WhiteSpace from '$/WhiteSpace.vue'
import VirtualKeyboardButton from './VirtualKeyboardButton.vue'

function click(n: number) {
  const key = String.fromCharCode('0'.charCodeAt(0) + n)
  const el = document.activeElement
  if (el instanceof HTMLElement && el.getAttribute('contenteditable') !== null) {
    const [selectionStart, selectionStop] = getSelectionPosition(el)
    assert(el.textContent !== null)
    el.textContent = el.textContent.slice(0, selectionStart) + key + el.textContent.slice(selectionStop)
    setCaretPosition(el, selectionStart + 1)
    el.dispatchEvent(new InputEvent('input', { inputType: '' }))
  } else {
    console.log('Active element not handled:', el)
  }
}

function getSelectionPosition(el: HTMLElement): [number, number] {
  const selection = document.getSelection()
  assert(selection !== null)
  const range = selection.getRangeAt(0)

  function resolve(container: Node, offset: number): number {
    while (container !== el) {
      let prev = container.previousSibling
      while (prev !== null) {
        if (prev instanceof Text) {
          offset += prev.length
        } else if (prev instanceof HTMLElement) {
          assert(prev.textContent !== null)
          offset += prev.textContent.length
        }
        prev = prev.previousSibling
      }
      const parent = container.parentElement
      assert(parent !== null)
      container = parent
    }
    return offset
  }
  return [resolve(range.startContainer, range.startOffset), resolve(range.endContainer, range.endOffset)]
}

function setCaretPosition(el: HTMLElement, caretPosition: number) {
  assert(el.childNodes.length == 1)
  const child = el.childNodes[0]
  assert(child instanceof Text)
  const range = document.createRange()
  const selection = document.getSelection()
  assert(selection !== null)
  range.setStart(child, caretPosition)
  range.setEnd(child, caretPosition)
  selection.removeAllRanges()
  selection.addRange(range)
}
</script>

<template>
  <template v-for="n in 10">
    <WhiteSpace />
    <VirtualKeyboardButton @click="click(n - 1)">{{ n - 1 }}</VirtualKeyboardButton>
  </template>
</template>
