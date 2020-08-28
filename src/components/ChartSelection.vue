<template>
  <b-container fluid="xl">
    <h2 class="my-3 font-weight-lighter text-left">Explore a Scenario</h2>
    <b-overlay :show="loadingScenarioList || loadingFailed">
      <template v-slot:overlay>
        <h3 v-if="loadingFailed">
          <fa-icon icon="exclamation-triangle" class="text-warning"></fa-icon>
          Failed to Load Scenarios
        </h3>
        <h4 v-else><b-spinner></b-spinner> Loading Scenarios</h4>
      </template>
      <b-nav pills class="mb-0">
        <b-nav-item
          v-for="(scenario, i) in tabScenarios"
          :key="'st-' + i"
          :active="selectedScenario === i"
          @click.prevent="selectedScenario = i"
          class="no-rounding"
        >
          {{ scenario.name }}
        </b-nav-item>
        <b-nav-item-dropdown
          id="dropdown-items"
          text="Other Scenarios"
          :active="selectedScenario >= numTabs"
          toggle-class="nav-link-custom rounded-0"
          class="dropdown-scroll rounded-0"
          :class="{ active: selectedScenario >= numTabs }"
          right
        >
          <b-dropdown-item
            v-for="(scenario, i) in dropdownScenarios"
            :key="'sd-' + (i + numTabs)"
            :active="selectedScenario === i + numTabs"
            @click.prevent="selectedScenario = i + numTabs"
          >
            {{ scenario.name }}
          </b-dropdown-item>
        </b-nav-item-dropdown>
        <b-nav-item
          v-if="selectedScenario >= numTabs"
          active
          @click.prevent=""
          class="no-rounding"
        >
          {{ scenarios[selectedScenario].name }}
        </b-nav-item>
      </b-nav>
      <chart
        v-if="scenarios.length"
        :scenario="scenarios[selectedScenario]"
        :key="'s-' + selectedScenario"
      ></chart>
    </b-overlay>
  </b-container>
</template>

<script>
import Chart from "./Chart"
import axios from "axios"

export default {
  name: "ChartSelection",
  components: {
    Chart
  },
  data() {
    return {
      scenarios: [],
      selectedScenario: 0,
      numTabs: 5,
      loadingScenarioList: true,
      loadingFailed: false
    }
  },
  mounted() {
    axios
      .get("https://biogearsengine.com/showcase/scenario_list.json")
      .then(response => {
        this.loadingScenarioList = false
        this.scenarios = response.data.scenarios
      })
      .catch(() => {
        this.loadingFailed = true
      })
  },
  computed: {
    tabScenarios() {
      return this.scenarios.slice(0, this.numTabs)
    },
    dropdownScenarios() {
      return this.scenarios.slice(this.numTabs)
    }
  }
}
</script>

<style scoped>
.no-rounding > a {
  border-radius: 0;
}

.dropdown-scroll /deep/ .dropdown-menu {
  max-height: 50vh;
  overflow-y: auto;
}
</style>
