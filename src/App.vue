<template>
  <div id="app">
    <!--    <img alt="BioGears logo" src="./assets/logo_410.png" />-->
    <!--    <prototype />-->
    <chart-selection></chart-selection>
    <!--    <showcase-player></showcase-player>-->
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
  margin-top: 60px;
}
</style>
