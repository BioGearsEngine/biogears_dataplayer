<template>
  <div>
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
          <!--          <g id="y-axis" :transform="'translate(' + margin.left + ',0)'"></g>-->
          <!--          <g-->
          <!--            v-for="key in enabledKeys"-->
          <!--            :key="'ya-' + keys.indexOf(key)"-->
          <!--            :id="'ya-' + keys.indexOf(key)"-->
          <!--            :transform="'translate(' + margin.left + ',0)'"-->
          <!--          ></g>-->
          <g id="x-axis"></g>
          <path
            v-for="series in enabledDataSeries"
            :key="'l-' + series.name"
            :id="'line-' + series.name"
            :d="series.line"
            fill="none"
            opacity="0.75"
            style="mix-blend-mode: darken"
            :stroke="
              isHovering && !(series.key === activeKey) ? '#ddd' : series.color
            "
            stroke-width="2"
            stroke-miterlimit="1"
            class="line"
            clip-path="url(#clip)"
          />
          <g
            id="dot"
            v-if="isHovering && dotPos"
            :transform="'translate(' + dotPos[0] + ',' + dotPos[1] + ')'"
          >
            <circle :r="dotRadius + 4" opacity="0.25"></circle>
            <circle :r="dotRadius + 1.5" fill="white"></circle>
            <circle :r="dotRadius" :fill="activeColor"></circle>
            <text
              font-family="sans-serif"
              font-size="10"
              text-anchor="middle"
              y="-25"
              style="background-color: white"
            >
              <tspan x="0" dy="0">{{ dotName }}</tspan>
              <tspan x="0" dy="1.2em" class="font-weight-bold">
                {{ dotVal }} {{ dotUnits }}
              </tspan>
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
            v-for="series in enabledDataSeries"
            :key="'nl-' + series.name"
            :id="'nav-line-' + series.name"
            :d="series.navLine"
            fill="none"
            opacity="0.5"
            :stroke="series.color"
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
      <!-- @click.stop="toggleKey(key)"-->
      <b-button
        v-for="(series, i) in dataSeries"
        :key="'toggle-key-' + i"
        variant="light"
        size="sm"
        @click.stop="toggleSeries(series)"
      >
        <fa-icon
          :icon="[series.enabled ? 'fas' : 'far', 'circle']"
          :style="{ color: series.color }"
        ></fa-icon>
        {{ series.name }}
      </b-button>
    </b-card>
  </div>
</template>

<script>
import * as d3 from "d3"

export default {
  name: "Chart",
  props: {
    scenario: {
      required: true
    }
  },
  data() {
    return {
      width: 1200,
      height: 425,
      navHeight: 115,
      margin: { top: 40, right: 40, bottom: 30, left: 40 },
      colors: [
        "#BF4141",
        "#D9BC4A",
        "#4EE662",
        "#96DCFF",
        "#A187E6",
        "#FF579A",
        "#FF8457",
        "#998C5A",
        "#57B0FF",
        "#3DB39B",
        "#FF96A4",
        "#9F4EE6",
        "#C6E687",
        "#996A34",
        "#30308C",
        "#347799"
      ],
      downscaleFactor: 1,
      navDownscaleFactor: 4,
      dataBuffer: 0.025,
      defaultNumSeriesEnabled: 4,
      defaultRangeInSeconds: 10,
      playbackIntervalId: "",
      playbackSpeed: 1,
      maxPlaybackSpeed: 32,
      playbackFrequency: 10,
      isPlaying: false,
      isHovering: false,
      lastMouseX: "",
      lastMouseY: "",
      dotPos: "",
      dotName: "",
      dotUnits: "",
      dotText: "",
      dotVal: "",
      dotRadius: 3.25,
      brush: "",
      currentSelectionRange: null,
      dataSeries: [],
      lines: [],
      navLines: [],
      keys: [],
      enabledKeys: [],
      activeKey: "",
      activeColor: "",
      xScale: null,
      xScaleNav: null,
      xAxis: null,
      xAxisNav: null
    }
  },
  computed: {
    marginLeft() {
      // calculate the sum of the label widths
      return 10
    },
    marginRight() {
      // calculate the sum of the label widths
      return 10
    },
    enabledDataSeries() {
      return this.dataSeries.filter(s => s.enabled)
    }
  },
  mounted() {
    this.loadData()
    this.setupBrush()
  },
  methods: {
    loadData() {
      let jsonData = JSON.parse(this.scenario.data)

      console.log()
      let xMin = Math.min(...Object.entries(jsonData).map(s => s[1][0][0]))
      let xMax = Math.max(
        ...Object.entries(jsonData).map(s => s[1][s[1].length - 1][0])
      )

      let xDomain = [xMin, xMax]
      if (!this.xScale) {
        this.updateXScale(xDomain)
      }
      if (!this.xScaleNav) {
        this.updateXScaleNav(xDomain)
      }

      let seriesCount = 0
      for (let [key, data] of Object.entries(jsonData)) {
        seriesCount++
        // let xDomain = d3.extent(data, d => d[0])
        // if (!this.xScale) {
        //   this.updateXScale(xDomain)
        // }
        // if (!this.xScaleNav) {
        //   this.updateXScaleNav(xDomain)
        // }

        let yDomain = d3.extent(jsonData[key], d => d[1])
        yDomain[0] -= Math.abs(yDomain[1] - yDomain[0]) * this.dataBuffer
        yDomain[1] += Math.abs(yDomain[1] - yDomain[0]) * this.dataBuffer
        let yScale = d3
          .scaleLinear()
          .domain(yDomain)
          .range([this.height - this.margin.bottom, this.margin.top])

        // TODO add the yAxis for each line
        // if (this.yScales.length === 1) {
        //   d3.select("#y-axis")
        //     .call(d3.axisLeft(yScale).ticks(2))
        //     .call(g =>
        //       g
        //         .selectAll(".tick line")
        //         .clone()
        //         .attr("stroke-opacity", d => (d === 1 ? null : 0.1))
        //         .attr("x2", this.width - this.margin.left - this.margin.right)
        //     )
        // }

        // set up each lines generator for the full chart
        let lineGenerator = d3
          .line()
          .x(d => this.xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)

        // set up each lines yScale for the nav chart
        let yNavScale = d3
          .scaleLinear()
          .domain(yDomain)
          .range([this.navHeight - this.margin.bottom, this.margin.top])

        // set up each lines generator for the nav chart
        let navLineGenerator = d3
          .line()
          .x(d => this.xScaleNav(d[0]))
          .y(d => yNavScale(d[1]))
          .curve(d3.curveMonotoneX)

        // downscale the nav lines further than the main chart
        let navDataPoints = this.largestTriangleThreeBuckets(
          data,
          Math.round(this.width / this.navDownscaleFactor)
        )

        let [name, units] = key.split("(")
        units = units ? units.split(")")[0] : ""

        // add the lines
        this.dataSeries.push({
          key: key,
          name: name,
          units: units,
          line: lineGenerator(data),
          lineGenerator: lineGenerator,
          yScale: yScale,
          navLine: navLineGenerator(navDataPoints),
          navLineGenerator: navLineGenerator,
          yNavScale: yNavScale,
          dataPoints: data,
          data: data,
          globalXDomain: xDomain,
          globalYDomain: yDomain,
          currentYDomain: yDomain,
          color: this.colors[(seriesCount - 1) % this.colors.length],
          enabled: seriesCount <= this.defaultNumSeriesEnabled,
          yAxisLeft: seriesCount % 2 === 1
        })

        // // TODO set up the y-axis for each line after it is added
        // let selector = "#ya-" + this.keys.indexOf(key)
        // console.log(selector)
        // let axis = d3.select("#ya-" + this.keys.indexOf(key))
        // console.log(axis)
        // d3.select("#ya-" + this.keys.indexOf(key))
        //   .call(d3.axisLeft(yScale))
        //   .call(g =>
        //     g
        //       .selectAll(".tick line")
        //       .clone()
        //       .attr("stroke-opacity", d => (d === 1 ? null : 0.1))
        //       .attr("x2", this.width - this.margin.left - this.margin.right)
        //   )
      }
    },
    updateXScale(extents) {
      this.xScale = d3
        .scaleLinear()
        .domain(extents)
        .range([this.margin.left, this.width - this.margin.right])
      this.updateXAxis()
    },
    updateXScaleNav(extents) {
      // x scale of nav is static, so keep it separate
      this.xScaleNav = d3
        .scaleLinear()
        .domain(extents)
        .range([this.margin.left, this.width - this.margin.right])
      this.updateXAxisNav()
    },
    updateXAxis() {
      // add the xAxis tick marks
      this.xAxis = (g, x) =>
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
      d3.select("#x-axis").call(this.xAxis, this.xScale)
    },
    updateXAxisNav() {
      // set up the x axis tick marks for the nav
      this.xAxisNav = g =>
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
      d3.select("#x-axis-nav").call(this.xAxisNav)
    },
    setupBrush() {
      // set up the brush
      this.brush = d3.brushX().extent([
        [this.margin.left, this.margin.top],
        [this.width - this.margin.right, this.navHeight - this.margin.bottom]
      ])

      this.brush.on("brush", () => {
        this.currentSelectionRange = d3.event.selection.map(
          this.xScaleNav.invert
        )
        console.log()
        if (d3.event.selection) {
          let newDomain = this.currentSelectionRange
          this.xScale.domain(newDomain)
          for (let series of this.dataSeries) {
            if (series.enabled) {
              this.updateSeries(series)
            }
          }
          // update the X Axis
          d3.select("#x-axis").call(this.xAxis, this.xScale)

          // if the chart changes, we need to update the tooltip as well
          if (this.isHovering) {
            this.updateTooltip()
          }
        }
      })

      let self = this
      // recenter the brush on a click
      let beforeBrushStarted = function() {
        let range = self.defaultRangeInSeconds
        if (self.currentSelectionRange) {
          range = self.currentSelectionRange[1] - self.currentSelectionRange[0]
        }
        console.log(range)
        const dx = self.xScaleNav(range) - self.xScaleNav(0)
        const [cx] = d3.mouse(this)
        const [x0, x1] = [cx - dx / 2, cx + dx / 2]
        const [X0, X1] = self.xScaleNav.range()
        d3.select(this.parentNode).call(
          self.brush.move,
          x1 > X1 ? [X1 - dx, X1] : x0 < X0 ? [X0, X0 + dx] : [x0, x1]
        )
      }

      // initialize the brush
      const g = d3.select("#brush")
      g.call(this.brush)
        .call(
          this.brush.move,
          [0, this.defaultRangeInSeconds].map(this.xScaleNav)
        )
        .call(g =>
          g
            .select(".overlay")
            .datum({ type: "selection" })
            .on("mousedown touchstart", beforeBrushStarted)
        )

      d3.select("#line-chart")
        .on("mousemove", function() {
          let mousePos = d3.mouse(this)
          self.lastMouseX = mousePos[0]
          self.lastMouseY = mousePos[1]
          self.updateTooltip()
        })
        .on("mouseenter", () => {
          this.isHovering = true
        })
        .on("mouseleave", () => {
          this.isHovering = false
        })
    },
    updateSeries(series) {
      // filter to only the portion of the line within the visible time frame, keeping any points that are
      // within the visible range, or where the next point before or after is in the visible range
      // TODO try doing the filter based on the number of points/second to get the indices of the new range
      // TODO or use binary search to find the index
      let newDomain = this.currentSelectionRange
      let points = series.data
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
      // down sample the lines
      points = this.largestTriangleThreeBuckets(
        points,
        Math.round(this.width / this.downscaleFactor)
      )

      // TODO if dynamic y scaling is enabled, update the line generator (try just updating the yScale first)

      series.dataPoints = points
      series.line = series.lineGenerator(points)
    },
    updateTooltip() {
      let min = Infinity
      const xm = this.lastMouseX
      const ym = this.lastMouseY

      let xmi = this.xScale.invert(xm)

      for (let series of this.enabledDataSeries) {
        // find the closest x index to this point
        let i1 = d3.bisectLeft(
          series.dataPoints.map(d => d[0]),
          xmi,
          1
        )
        let i0 = i1 - 1

        let i
        if (i1 >= series.dataPoints.length) {
          i = i0
        } else {
          i =
            xm - this.xScale(series.dataPoints[i0][0]) >
            this.xScale(series.dataPoints[i1][0]) - xm
              ? i1
              : i0
        }
        let yDist

        // TODo this only fixes part of the problem... the points can still be outside the margins
        if (!series.dataPoints[i]) {
          yDist = Math.Infinity
        } else {
          yDist = Math.abs(series.yScale(series.dataPoints[i][1]) - ym)
        }

        if (yDist < min) {
          min = yDist
          this.activeKey = series.key
          this.activeColor = series.color
          this.dotPos = [
            this.xScale(series.dataPoints[i][0]),
            series.yScale(series.dataPoints[i][1])
          ]
          this.dotText = series.key
          this.dotName = series.name
          this.dotUnits = series.units
          this.dotVal = series.dataPoints[i][1]
          d3.select("#line-" + this.keys.indexOf(series.key)).raise()
          d3.select("#dot").raise()
        }
      }
    },
    toggleSeries(series) {
      series.enabled = !series.enabled
      if (series.enabled) {
        this.updateSeries(series)
      }
      // TODO also needs to toggle the yAxis for each line
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
        let range = this.currentSelectionRange
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
      let range = this.currentSelectionRange
      let rangeSize = range[1] - range[0]
      d3.select("#brush").call(
        this.brush.move,
        [domain[0], domain[0] + rangeSize].map(this.xScaleNav)
      )
    },
    jumpToEnd() {
      this.stopPlayback()
      let domain = this.xScaleNav.domain()
      let range = this.currentSelectionRange
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
        let range_offs = floor(i * every) + 1,
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
