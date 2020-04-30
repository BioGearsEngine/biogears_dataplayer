<template>
  <div id="app">
    <!--    <img alt="BioGears logo" src="./assets/logo_410.png" />-->
    <!--    <prototype />-->
    <chart />
  </div>
</template>

<script>
import Chart from "./components/Chart"
// import Prototype from "./components/Prototype"

export default {
  name: "App",
  components: {
    Chart
    // Prototype
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
