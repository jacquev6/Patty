<template>
  <div class="columns">
    <div class="column">
      <slot name="left"></slot>
    </div>
    <div class="gutter"></div>
    <div class="column">
      <slot name="center"></slot>
    </div>
    <div class="gutter"></div>
    <div class="column">
      <slot name="right"></slot>
    </div>
  </div>
</template>

<style scoped>
.columns {
  display: grid;
  grid-template-columns: 1fr 2px 1fr 2px 1fr;
  height: 100vh;
  overflow-y: hidden;
}

.gutter {
  background-color: black;
}

.column {
  padding-left: 5px;
  padding-right: 5px;
  overflow-y: scroll;
}
</style>
