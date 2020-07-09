<template>
  <b-container fluid>
    <h3 class="mt-2">Explore a Scenario</h3>
    <b-nav pills class="mb-0">
      <b-nav-item
        v-for="(scenario, i) in scenarios"
        :key="'s-' + i"
        :active="selectedScenario === i"
        @click.prevent="selectedScenario = i"
        class="no-rounding"
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

import { MULTI_TRAUMA_DATA } from "../static/multi-trauma-datafile"
import { EXPOSURE_DATA } from "../static/exposure-datafile"
import { ASTHMA_DATA } from "../static/asthma-datafile"
import { HEAT_STROKE_DATA } from "../static/heat-stroke-datafile"
import { SEPSIS_DATA } from "../static/sepsis-datafile"

import { MULTI_TRAUMA_LOG } from "../static/multi-trauma-logfile"
import { EXPOSURE_LOG } from "../static/exposure-logfile"
import { ASTHMA_LOG } from "../static/asthma-logfile"
import { HEAT_STROKE_LOG } from "../static/heat-stroke-logfile"
import { SEPSIS_LOG } from "../static/sepsis-logfile"

export default {
  name: "ChartSelection",
  components: {
    Chart
  },
  data() {
    return {
      scenarios: [
        {
          name: "Multi-Trauma",
          data: MULTI_TRAUMA_DATA,
          logs: MULTI_TRAUMA_LOG
        },
        { name: "Exposure", data: EXPOSURE_DATA, logs: EXPOSURE_LOG },
        { name: "Asthma", data: ASTHMA_DATA, logs: ASTHMA_LOG },
        { name: "Heat Stroke", data: HEAT_STROKE_DATA, logs: HEAT_STROKE_LOG },
        { name: "Sepsis", data: SEPSIS_DATA, logs: SEPSIS_LOG }
      ],
      selectedScenario: 0
    }
  }
}
</script>

<style scoped>
.no-rounding > a {
  border-radius: 0;
}
</style>
