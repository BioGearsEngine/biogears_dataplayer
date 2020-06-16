<template>
  <div>
    <b-container fluid>
      <h3>Explore a Scenario</h3>
      <b-nav tabs class="mb-2">
        <b-nav-item>Multi-Trauma</b-nav-item>
        <b-nav-item>Exposure</b-nav-item>
        <b-nav-item active>Asthma</b-nav-item>
        <b-nav-item>Heat Stroke</b-nav-item>
        <b-nav-item>Sepsis</b-nav-item>
        <b-nav-item>Upload a Scenario</b-nav-item>
      </b-nav>
      <b-card class="mb-2" no-body>
        <b-card-body>
          <svg
            id="line-chart"
            :viewBox="'0 0 ' + width + ' ' + height"
            style="background: #fff"
            class="mb-2"
          >
            <clipPath id="clip">
              <rect
                :x="margin.left"
                :y="margin.top"
                :width="width - margin.left - margin.right"
                :height="height - margin.top - margin.bottom"
              ></rect>
            </clipPath>
            <g
              v-for="key in enabledKeys"
              :key="'ya-' + keys.indexOf(key)"
              :id="'ya-' + keys.indexOf(key)"
              :transform="'translate(' + margin.left + ',0)'"
            ></g>
            <g id="x-axis"></g>
            <path
              v-for="(line, index) in enabledLines"
              :key="'l-' + index"
              :id="'line-' + keys.indexOf(line.key)"
              :d="line.points"
              fill="none"
              opacity="1"
              :stroke="
                isHovering && !(line.key === activeKey) ? '#ddd' : line.color
              "
              stroke-width="2.5"
              stroke-miterlimit="1"
              class="line"
              clip-path="url(#clip)"
            />
            <g
              id="dot"
              v-if="showDot"
              :transform="'translate(' + dotPos[0] + ',' + dotPos[1] + ')'"
            >
              <circle :r="dotRadius + 4" opacity="0.25"></circle>
              <circle :r="dotRadius + 1.5" fill="white"></circle>
              <circle :r="dotRadius" :fill="activeColor"></circle>
              <text
                font-family="sans-serif"
                font-size="10"
                text-anchor="middle"
                y="-8"
              >
                {{ dotText }}: {{ dotVal }}
              </text>
            </g>
          </svg>
          <svg
            id="nav-bar"
            :viewBox="'0 0 ' + width + ' ' + navHeight"
            style="background: #fff"
          >
            <g id="x-axis-nav"></g>
            <path
              v-for="(line, index) in enabledNavLines"
              :key="'nl-' + index"
              :d="line.points"
              fill="none"
              opacity="0.5"
              :stroke="line.color"
              stroke-width="1"
              stroke-miterlimit="1"
              class="nav-line"
            />
            <g id="brush" />
          </svg>
        </b-card-body>
        <b-card-footer>
          <b-button-toolbar class="justify-content-center">
            <b-button-group size="sm" class="mx-1">
              <b-button variant="outline-dark" @click.stop="jumpToBeginning()">
                <fa-icon icon="fast-backward"></fa-icon>
              </b-button>
            </b-button-group>
            <b-button-group size="sm" class="mx-1">
              <b-button
                variant="outline-dark"
                :disabled="playbackSpeed === -maxPlaybackSpeed"
                @click.stop="decreaseSpeed()"
              >
                <fa-icon icon="backward"></fa-icon>
              </b-button>
              <b-button variant="outline-dark" @click.stop="togglePlayback()">
                <fa-icon :icon="isPlaying ? 'pause' : 'play'"></fa-icon>
              </b-button>
              <b-button
                variant="outline-dark"
                :disabled="playbackSpeed === maxPlaybackSpeed"
                @click.stop="increaseSpeed()"
              >
                <fa-icon icon="forward"></fa-icon>
              </b-button>
            </b-button-group>
            <b-button-group size="sm" class="mx-1">
              <b-button variant="outline-dark" @click.stop="jumpToEnd()">
                <fa-icon icon="fast-forward"></fa-icon>
              </b-button>
            </b-button-group>
            <b-button-group size="sm" class="mx-1">
              <b-button variant="outline-dark" style="width: 46px" disabled>
                {{ playbackSpeed }}x
              </b-button>
            </b-button-group>
          </b-button-toolbar>
        </b-card-footer>
      </b-card>
      <b-card>
        <b-button
          v-for="(key, i) in keys"
          :key="'toggle-key-' + i"
          variant="light"
          @click.stop="toggleKey(key)"
        >
          <fa-icon
            :icon="[enabledKeys.includes(key) ? 'fas' : 'far', 'circle']"
            :style="{ color: colors[i % colors.length] }"
          ></fa-icon>
          {{ key }}
        </b-button>
      </b-card>
    </b-container>
  </div>
</template>

<script>
export default {
  name: "ShowcasePlayer"
}
</script>

<style scoped></style>
