<template>
  <b-container fluid="xl">
    <h2 class="my-3 font-weight-lighter text-left">Explore a Scenario</h2>
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
      :scenario="scenarios[selectedScenario]"
      :key="'s-' + selectedScenario"
    ></chart>
  </b-container>
</template>

<script>
// import Chart from "./Chart"
import Chart from "./NewChart"

export default {
  name: "ChartSelection",
  components: {
    Chart
  },
  data() {
    return {
      scenarios: [
        { name: "Multi-Trauma", filename: "Multi-Trauma" },
        { name: "Exposure", filename: "Exposure" },
        { name: "Asthma", filename: "Asthma" },
        { name: "Heat Stroke", filename: "HeatStroke" },
        { name: "Sepsis", filename: "Sepsis" },
        { name: "Acute Stress", filename: "AcuteStressResults" },
        {
          name: "Airway Obstruction",
          filename: "AirwayObstructionVariedResults"
        },
        { name: "Anemia 30", filename: "Anemia30Results" },
        { name: "Apnea Varied", filename: "ApneaVariedResults" },
        {
          name: "Asthma Attack Life Threatening Acute",
          filename: "AsthmaAttackLifeThreateningAcuteResults"
        },
        {
          name: "Asthma Attack Moderate Acute",
          filename: "AsthmaAttackModerateAcuteResults"
        },
        {
          name: "Asthma Attack Severe Acute",
          filename: "AsthmaAttackSevereAcuteResults"
        },
        { name: "Baroreceptors", filename: "BaroreceptorsResults" },
        { name: "Basic Standard", filename: "BasicStandardResults" },
        { name: "Brain Injury", filename: "BrainInjuryResults" },
        {
          name: "Broncho Constriction Varied",
          filename: "BronchoConstrictionVariedResults"
        },
        {
          name: "COPD Severe Bronchitis",
          filename: "COPDSevereBronchitisResults"
        },
        {
          name: "COPD Severe Emphysema",
          filename: "COPDSevereEmphysemaResults"
        },
        { name: "Cough", filename: "CoughResults" },
        { name: "CPR Force", filename: "CPRForceResults" },
        { name: "CPR Force Scale Max", filename: "CPRForceScaleMaxResults" },
        { name: "CPR Force Scale", filename: "CPRForceScaleResults" },
        { name: "Dehydrate", filename: "DehydrateResults" },
        {
          name: "Effusion Condition Plus",
          filename: "EffusionConditionPlusResults"
        },
        { name: "Effusion Condition", filename: "EffusionConditionResults" },
        {
          name: "Esophageal Intubation",
          filename: "EsophagealIntubationResults"
        },
        {
          name: "Hemorrhage Class 2 Blood",
          filename: "HemorrhageClass2BloodResults"
        },
        {
          name: "Hemorrhage Class 2 No Fluid",
          filename: "HemorrhageClass2NoFluidResults"
        },
        {
          name: "Hemorrhage Class 2 Saline",
          filename: "HemorrhageClass2SalineResults"
        },
        {
          name: "Hemorrhage Class 4 No Fluid",
          filename: "HemorrhageClass4NoFluidResults"
        },
        { name: "Hemorrhage CM1", filename: "HemorrhageCM1Results" },
        { name: "Hemorrhage CM2", filename: "HemorrhageCM2Results" },
        { name: "Infection Mild", filename: "InfectionMildResults" },
        { name: "Infection Moderate", filename: "InfectionModerateResults" },
        { name: "Infection Severe", filename: "InfectionSevereResults" },
        {
          name: "Inhaler - One Actuation Incorrect Use",
          filename: "Inhaler_OneActuationIncorrectUseResults"
        },
        {
          name: "Inhaler - One Actuation",
          filename: "Inhaler_OneActuationResults"
        },
        {
          name: "Inhaler - One Actuation with Spacer Incorrect Use",
          filename: "Inhaler_OneActuationWithSpacerIncorrectUseResults"
        },
        {
          name: "Inhaler - One Actuation with Spacer",
          filename: "Inhaler_OneActuationWithSpacerResults"
        },
        {
          name: "Inhaler - Two Actuations",
          filename: "Inhaler_TwoActuationsResults"
        },
        { name: "IV Fluids", filename: "IVFluidsResults" },
        {
          name: "Lobar Pneumonia Moderate Both Lungs",
          filename: "LobarPneumoniaModerateBothLungsResults"
        },
        {
          name: "Lobar Pneumonia Severe Left Lobe",
          filename: "LobarPneumoniaSevereLeftLobeResults"
        },
        {
          name: "Lobar Pneumonia Severe Right Lung",
          filename: "LobarPneumoniaSevereRightLungResults"
        },
        { name: "Mainstem Intubation", filename: "MainstemIntubationResults" },
        {
          name: "Pain Stimulus Moderate",
          filename: "PainStimulusModerateResults"
        },
        {
          name: "Renal Stenosis Moderate Unilateral",
          filename: "RenalStenosisModerateUnilateralResults"
        },
        {
          name: "Renal Stenosis Severe Bilateral",
          filename: "RenalStenosisSevereBilateralResults"
        },
        { name: "Saline Infusion Results", filename: "SalineInfusionResults" },
        { name: "Sepsis Severe - Gut", filename: "SepsisSevere_GutResults" },
        { name: "Sinus Bradycardia", filename: "SinusBradycardiaResults" },
        { name: "Sinus Tachycardia", filename: "SinusTachycardiaResults" },
        {
          name: "Tension Pneumothorax Bilateral",
          filename: "TensionPneumothoraxBilateralResults"
        },
        {
          name: "Tension Pneumothorax Closed Varied",
          filename: "TensionPneumothoraxClosedVariedResults"
        },
        {
          name: "Tension Pneumothorax Open Varied",
          filename: "TensionPneumothoraxOpenVariedResults"
        },
        {
          name: "TXA Low Hemorrhage Results",
          filename: "TXALowHemorrhageResults"
        },
        {
          name: "Ventricular Systolic Dysfunction",
          filename: "VentricularSystolicDysfunctionResults"
        }
      ],
      selectedScenario: 0,
      numTabs: 5
    }
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
