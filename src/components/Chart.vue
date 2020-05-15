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
        <!--        <b-card-header header-tag="nav">-->
        <!--          <b-nav card-header tabs>-->
        <!--            <b-nav-item>Multi-Trauma</b-nav-item>-->
        <!--            <b-nav-item>Exposure</b-nav-item>-->
        <!--            <b-nav-item active>Asthma</b-nav-item>-->
        <!--            <b-nav-item>Heat Stroke</b-nav-item>-->
        <!--            <b-nav-item>Sepsis</b-nav-item>-->
        <!--            <b-nav-item>Upload a Scenario</b-nav-item>-->
        <!--          </b-nav>-->
        <!--        </b-card-header>-->
        <b-card-body>
          <svg
            id="line-chart"
            :width="width"
            :height="height"
            style="background: #fafafa"
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
            :width="width"
            :height="navHeight"
            style="background: #fafafa"
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
import * as d3 from "d3"

// import { SEPSIS_JSON as DATAFILE } from "../static/sepsis-datafile"
import { EXPOSURE_JSON as DATAFILE } from "../static/exposure-datafile"
// import { ASTHMA_JSON as DATAFILE } from "../static/asthma-datafile"

export default {
  name: "Chart.vue",
  data() {
    return {
      width: 1600,
      navMargin: {
        top: 10,
        right: 20,
        bottom: 20,
        left: 20
      },
      navHeight: 120,
      height: 600,
      margin: { top: 20, right: 20, bottom: 30, left: 30 },
      lines: [],
      navLines: [],
      colors: [
        "#56a0bf",
        "#494c7c",
        "#bf8bb9",
        "#506631",
        "#c48466",
        "#76332d",
        "#67b389",
        "#723076",
        "#c49b3f",
        "#7175d6",
        "#d14a76",
        "#73b643",
        "#d24e30",
        "#d151c3",
        "#763cc8"
      ],
      brush: "",
      currentSelection: "",
      downscaleFactor: 2,
      navDownscaleFactor: 4,
      defaultRangeInSeconds: 10,
      keys: [],
      enabledKeys: [],
      activeKey: "",
      activeColor: "",
      playbackIntervalId: "",
      playbackSpeed: 1,
      maxPlaybackSpeed: 16,
      playbackFrequency: 10,
      isPlaying: false,
      xScale: "",
      xScaleNav: "",
      isHovering: false,
      lastMouseX: "",
      lastMouseY: "",
      dotPos: [],
      dotText: "",
      dotVal: "",
      dotRadius: 3.25,
      showDot: false
    }
  },
  computed: {
    enabledLines() {
      return this.lines.filter(l => this.enabledKeys.includes(l.key))
    },
    enabledNavLines() {
      return this.navLines.filter(l => this.enabledKeys.includes(l.key))
    }
  },
  mounted() {
    this.drawCharts()
  },
  methods: {
    drawCharts() {
      let jsonData = JSON.parse(DATAFILE)
      this.keys = Object.keys(jsonData)

      // TODO may need to check for actual min/max
      this.xScale = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[this.keys[0]], d => d[0]))
        .range([this.margin.left, this.width - this.margin.right])

      // add the xAxis tick marks
      let xAxis = (g, x) =>
        g
          .attr("transform", `translate(0,${this.height - this.margin.bottom})`)
          .call(
            d3
              .axisBottom(x)
              .ticks(this.width / 80)
              // .ticks(10)
              .tickSizeOuter(0)
              .tickFormat(this.toMMSS)
          )
      d3.select("#x-axis").call(xAxis, this.xScale)

      // x scale of nav is static, so keep it separate
      this.xScaleNav = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[this.keys[0]], d => d[0]))
        .range([this.margin.left, this.width - this.margin.right])

      // set up the x axis tick marks for the nav
      let xAxisNav = g =>
        g
          .attr(
            "transform",
            `translate(0,${this.navHeight - this.margin.bottom})`
          )
          .call(
            d3
              .axisBottom(this.xScaleNav)
              .ticks(this.width / 80)
              .tickSizeOuter(0)
              .tickFormat(this.toMMSS)
          )
      d3.select("#x-axis-nav").call(xAxisNav)

      let yScales = []
      let yNavScales = []
      let navLineGenerators = []
      let lineGenerators = []
      for (let key of this.keys) {
        // set up each lines yScale for the full chart
        let yScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.height - this.margin.bottom, this.margin.top])
        yScales.push(yScale)

        // TODO add the yAxis for each line

        // set up each lines generator for the full chart
        let lineGenerator = d3
          .line()
          .x(d => this.xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)
        lineGenerators.push(lineGenerator)
        // add the lines
        this.lines.push({
          points: lineGenerator(jsonData[key]),
          key: key,
          color: this.colors[this.lines.length % this.colors.length],
          generator: lineGenerator,
          yScale: yScale,
          dataPoints: jsonData[key]
        })
        this.enabledKeys.push(key)

        // set up each lines yScale for the nav chart
        let yNavScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.navHeight - this.margin.bottom, this.margin.top])
        yNavScales.push(yNavScale)
        // set up each lines generator for the nav chart
        let navLineGenerator = d3
          .line()
          .x(d => this.xScaleNav(d[0]))
          .y(d => yNavScale(d[1]))
          .curve(d3.curveMonotoneX)
        navLineGenerators.push(navLineGenerator)
        // downscale the nav lines further than the main chart
        let points = this.largestTriangleThreeBuckets(
          jsonData[key],
          Math.round(this.width / this.navDownscaleFactor)
        )
        this.navLines.push({
          points: navLineGenerator(points),
          key: key,
          color: this.colors[this.navLines.length % this.colors.length]
        })
      }
      // }

      // set up the brush
      const brush = d3.brushX().extent([
        [this.margin.left, this.margin.top],
        [this.width - this.margin.right, this.navHeight - this.margin.bottom]
      ])
      this.brush = brush

      brush.on("brush", () => {
        // console.log("brush")
        this.currentSelection = d3.event.selection
        if (d3.event.selection) {
          let newDomain = d3.event.selection.map(this.xScaleNav.invert)
          this.xScale.domain(newDomain)
          for (let line of this.lines) {
            if (this.enabledKeys.includes(line.key)) {
              // filter to only the portion of the line within the visible time frame, keeping any points that are
              // within the visible range, or where the next point before or after is in the visible range
              // TODO try doing the filter based on the number of points/second to get the indices of the new range
              let points = jsonData[line.key]
              points = points.filter((a, index) => {
                // point in visible range
                if (a[0] >= newDomain[0] && a[0] <= newDomain[1]) {
                  return true
                } else if (
                  // next point in visible range
                  points[index + 1] &&
                  points[index + 1][0] >= newDomain[0] &&
                  points[index + 1][0] <= newDomain[1]
                ) {
                  return true
                } else {
                  return (
                    // previous point in visible range
                    points[index - 1] &&
                    points[index - 1][0] >= newDomain[0] &&
                    points[index - 1][0] <= newDomain[1]
                  )
                }
              })
              // downscale the lines
              points = this.largestTriangleThreeBuckets(
                points,
                Math.round(this.width / this.downscaleFactor)
              )
              line.dataPoints = points
              line.points = line.generator(points)
            }
          }
          d3.select("#x-axis").call(xAxis, this.xScale)
          if (this.isHovering) {
            this.updateTooltip()
          }
        }
      })

      // TODO fix needing this?
      let self = this
      // recenter the brush on a click
      let beforeBrushStarted = function() {
        let range = self.defaultRangeInSeconds
        if (self.currentSelection) {
          let selection = self.currentSelection.map(self.xScaleNav.invert)
          range = selection[1] - selection[0]
        }
        const dx = self.xScaleNav(range) - self.xScaleNav(0)
        const [cx] = d3.mouse(this)
        const [x0, x1] = [cx - dx / 2, cx + dx / 2]
        const [X0, X1] = self.xScaleNav.range()
        d3.select(this.parentNode).call(
          brush.move,
          x1 > X1 ? [X1 - dx, X1] : x0 < X0 ? [X0, X0 + dx] : [x0, x1]
        )
      }

      // initialize the brush
      const g = d3.select("#brush")
      g.call(brush)
        .call(brush.move, [0, this.defaultRangeInSeconds].map(this.xScaleNav))
        .call(g =>
          g
            .select(".overlay")
            .datum({ type: "selection" })
            .on("mousedown touchstart", beforeBrushStarted)
        )

      // TODO enable the mouse hover events
      d3.select("#line-chart")
        .on("mousemove", this.moved)
        .on("mouseenter", this.entered)
        .on("mouseleave", this.left)
    },
    updateTooltip() {
      this.showDot = false
      let min = Infinity
      const xm = this.lastMouseX - (this.margin.left + this.dotRadius)
      const ym = this.lastMouseY - (this.margin.top + this.dotRadius)
      let xmi = this.xScale.invert(xm)

      for (let line of this.enabledLines) {
        // find the closest x index to this point
        let i1 = d3.bisectLeft(
          line.dataPoints.map(d => d[0]),
          xmi,
          1
        )
        let i0 = i1 - 1

        let i
        if (i1 >= line.dataPoints.length) {
          i = i0
        } else {
          i =
            xm - this.xScale(line.dataPoints[i0][0]) >
            this.xScale(line.dataPoints[i1][0]) - xm
              ? i1
              : i0
        }

        let yDist = Math.abs(line.yScale(line.dataPoints[i][1]) - ym)

        if (yDist < min) {
          min = yDist
          this.activeKey = line.key
          this.activeColor = line.color
          this.dotPos = [
            this.xScale(line.dataPoints[i][0]),
            line.yScale(line.dataPoints[i][1])
          ]
          this.dotText = line.key
          this.dotVal = line.dataPoints[i][1]
          d3.select("#line-" + this.keys.indexOf(line.key)).raise()
          d3.select("#dot").raise()
        }
      }
      this.showDot = true
    },
    moved() {
      d3.event.preventDefault()
      this.lastMouseX = d3.event.layerX
      this.lastMouseY = d3.event.layerY
      this.updateTooltip()
    },
    entered() {
      // console.log("entered")
      this.isHovering = true
    },
    left() {
      // console.log("left")
      this.isHovering = false
      this.showDot = false
    },
    toggleKey(key) {
      // TODO also needs to toggle the yAxis for each line
      // console.log("toggling key: " + key)
      let index = this.enabledKeys.indexOf(key)
      if (index !== -1) {
        this.enabledKeys.splice(index, 1)
        this.lines[this.keys.indexOf(key)].points = ""
      } else {
        // TODO need to update the line
        this.enabledKeys.push(key)
      }
    },
    togglePlayback() {
      if (this.isPlaying) {
        this.stopPlayback()
      } else {
        this.startPlayback()
      }
    },
    stopPlayback() {
      if (this.isPlaying) {
        clearInterval(this.playbackIntervalId)
        this.isPlaying = false
      }
    },
    startPlayback() {
      this.playbackIntervalId = setInterval(() => {
        let range = this.currentSelection.map(this.xScaleNav.invert)
        let newRange = [
          range[0] + (1 / this.playbackFrequency) * this.playbackSpeed,
          range[1] + (1 / this.playbackFrequency) * this.playbackSpeed
        ]
        // check for the beginning and end
        let domain = this.xScaleNav.domain()
        if (newRange[0] < domain[0]) {
          let rangeSize = newRange[1] - newRange[0]
          newRange = [domain[0], domain[0] + rangeSize]
          this.stopPlayback()
        } else if (newRange[1] > domain[1]) {
          let rangeSize = newRange[1] - newRange[0]
          newRange = [domain[1] - rangeSize, domain[1]]
          this.stopPlayback()
        }
        // TODO add a transition to make it smoother?
        d3.select("#brush").call(this.brush.move, newRange.map(this.xScaleNav))
      }, 1000 / this.playbackFrequency)
      this.isPlaying = true
    },
    increaseSpeed() {
      if (this.playbackSpeed > 0) {
        this.playbackSpeed *= 2
      } else {
        if (this.playbackSpeed === -1) {
          this.playbackSpeed *= -1
        } else {
          this.playbackSpeed /= 2
        }
      }
    },
    decreaseSpeed() {
      if (this.playbackSpeed < 0) {
        this.playbackSpeed *= 2
      } else {
        if (this.playbackSpeed === 1) {
          this.playbackSpeed *= -1
        } else {
          this.playbackSpeed /= 2
        }
      }
    },
    jumpToBeginning() {
      this.stopPlayback()
      let domain = this.xScaleNav.domain()
      let range = this.currentSelection.map(this.xScaleNav.invert)
      let rangeSize = range[1] - range[0]
      d3.select("#brush").call(
        this.brush.move,
        [domain[0], domain[0] + rangeSize].map(this.xScaleNav)
      )
    },
    jumpToEnd() {
      this.stopPlayback()
      let domain = this.xScaleNav.domain()
      let range = this.currentSelection.map(this.xScaleNav.invert)
      let rangeSize = range[1] - range[0]
      d3.select("#brush").call(
        this.brush.move,
        [domain[1] - rangeSize, domain[1]].map(this.xScaleNav)
      )
    },
    largestTriangleThreeBuckets(data, threshold) {
      let floor = Math.floor
      let abs = Math.abs

      let data_length = data.length
      if (threshold >= data_length || threshold === 0) {
        return data // Nothing to do
      }

      let sampled = [],
        sampled_index = 0

      // Bucket size. Leave room for start and end data points
      let every = (data_length - 2) / (threshold - 2)

      let a = 0, // Initially a is the first point in the triangle
        max_area_point,
        max_area,
        area,
        next_a

      sampled[sampled_index++] = data[a] // Always add the first point

      for (let i = 0; i < threshold - 2; i++) {
        // Calculate point average for next bucket (containing c)
        let avg_x = 0,
          avg_y = 0,
          avg_range_start = floor((i + 1) * every) + 1,
          avg_range_end = floor((i + 2) * every) + 1
        avg_range_end =
          avg_range_end < data_length ? avg_range_end : data_length

        let avg_range_length = avg_range_end - avg_range_start

        for (; avg_range_start < avg_range_end; avg_range_start++) {
          avg_x += data[avg_range_start][0] * 1 // * 1 enforces Number (value may be Date)
          avg_y += data[avg_range_start][1] * 1
        }
        avg_x /= avg_range_length
        avg_y /= avg_range_length

        // Get the range for this bucket
        let range_offs = floor((i + 0) * every) + 1,
          range_to = floor((i + 1) * every) + 1

        // Point a
        let point_a_x = data[a][0] * 1, // enforce Number (value may be Date)
          point_a_y = data[a][1] * 1

        max_area = area = -1

        for (; range_offs < range_to; range_offs++) {
          // Calculate triangle area over three buckets
          area =
            abs(
              (point_a_x - avg_x) * (data[range_offs][1] - point_a_y) -
                (point_a_x - data[range_offs][0]) * (avg_y - point_a_y)
            ) * 0.5
          if (area > max_area) {
            max_area = area
            max_area_point = data[range_offs]
            next_a = range_offs // Next a is this b
          }
        }

        sampled[sampled_index++] = max_area_point // Pick this point from the bucket
        a = next_a // This a is the next a (chosen b)
      }

      sampled[sampled_index++] = data[data_length - 1] // Always add last

      return sampled
    },
    toMMSS(second) {
      // second = parseInt(second, 10)
      let seconds = second % 60
      if (seconds < 10) {
        seconds = "0" + seconds
      }
      return Math.floor(second / 60) + ":" + seconds
    }
  }
}
</script>

<style scoped></style>
