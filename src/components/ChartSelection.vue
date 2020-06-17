<template>
  <b-container fluid>
    <h3>Explore a Scenario</h3>
    <b-nav tabs class="mb-2">
      <b-nav-item
        v-for="(scenario, i) in scenarios"
        :key="'s-' + i"
        :active="selectedScenario === i"
        @click.prevent="selectedScenario = i"
      >
        {{ scenario.name }}
      </b-nav-item>
    </b-nav>
    <chart
      :scenario="scenarios[selectedScenario]"
      :key="'s-' + selectedScenario"
    ></chart>
  </b-container>
</template>

<script>
// import Chart from "./Chart"
import Chart from "./NewChart"

import { MULTI_TRAUMA_DATA } from "../static/multi-trauma"
import { EXPOSURE_DATA } from "../static/exposure-datafile"
import { ASTHMA_DATA } from "../static/asthma-datafile"
import { HEAT_STROKE_DATA } from "../static/heat-stroke"
import { SEPSIS_DATA } from "../static/sepsis-datafile"

export default {
  name: "ChartSelection",
  components: {
    Chart
  },
  data() {
    return {
      scenarios: [
        { name: "Multi-Trauma", data: MULTI_TRAUMA_DATA },
        { name: "Exposure", data: EXPOSURE_DATA },
        { name: "Asthma", data: ASTHMA_DATA },
        { name: "Heat Stroke", data: HEAT_STROKE_DATA },
        { name: "Sepsis", data: SEPSIS_DATA }
      ],
      selectedScenario: 0
    }
  }
}
</script>

<style scoped></style>
