<template>
  <div id="app">
    <chart-selection></chart-selection>
  </div>
</template>

<script>
import ChartSelection from "./components/ChartSelection"

export default {
  name: "App",
  components: {
    ChartSelection
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
