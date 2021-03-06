<template>
  <div>
    <b-overlay :show="downloadingScenario || loadingFailed">
      <template v-slot:overlay>
        <h4 v-if="loadingFailed">
          <fa-icon icon="exclamation-triangle" class="text-warning"></fa-icon>
          Failed to Load Scenario
        </h4>
        <h4 v-else><b-spinner></b-spinner> Loading Scenario</h4>
      </template>

      <b-card class="mb-2 rounded-0" no-body>
        <b-card-body>
          <!-- the main line chart -->
          <svg
            id="line-chart"
            :viewBox="'0 0 ' + width + ' ' + height"
            style="background: #fff"
            class="mb-2"
          >
            <!-- clipping path for the data series -->
            <clipPath id="clip">
              <rect
                :x="marginLeft"
                :y="margin.top"
                :width="width - marginLeft - marginRight"
                :height="height - margin.top - margin.bottom"
              ></rect>
            </clipPath>

            <!-- clipping path for the event flags -->
            <clipPath id="clip2">
              <rect
                :x="marginLeft"
                y="0"
                :width="width - marginLeft - marginRight"
                :height="height - margin.bottom"
              ></rect>
            </clipPath>

            <!-- the background y-axis lines -->
            <g id="background-ticks" clip-path="url(#clip)"></g>

            <!-- dynamic y-axes for each data series -->
            <g
              v-for="series in dataSeries"
              v-show="series.enabled"
              :key="`ya-${series.index}-${series.name}`"
              :id="`ya-${series.index}-${series.name}`"
            >
              <text :id="`tl-${series.index}-${series.name}`"></text>
            </g>

            <g id="x-axis"></g>

            <!-- data series paths -->
            <path
              v-for="series in enabledDataSeries"
              :key="`l-${series.index}-${series.name}`"
              :id="`line-${series.index}-${series.name}`"
              :d="series.line"
              fill="none"
              opacity="0.75"
              style="mix-blend-mode: darken"
              :stroke="
                isHovering && !(series.key === activeKey)
                  ? '#ddd'
                  : series.color
              "
              stroke-width="2"
              stroke-miterlimit="1"
              class="line"
              clip-path="url(#clip)"
            />

            <!-- log entry flags -->
            <g clip-path="url(#clip2)">
              <template v-for="category in logCategories">
                <log-flag
                  v-for="(entry, index) in category.entries"
                  v-show="category.enabled"
                  :key="'log-' + category.name + '-' + index"
                  :x-pos="xScale(entry.time)"
                  :height="height - margin.bottom"
                  :category="category"
                  :entry="entry"
                  :index="index"
                ></log-flag>
              </template>
            </g>

            <!-- mouse hover tooltip -->
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

          <!-- the nav bar line chart -->
          <svg
            id="nav-bar"
            :viewBox="'0 0 ' + width + ' ' + navHeight"
            style="background: #fff"
          >
            <g id="x-axis-nav"></g>
            <path
              v-for="series in enabledDataSeries"
              :key="`nl-${series.index}-${series.name}`"
              :id="`nav-line-${series.index}-${series.name}`"
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

        <!-- playback controls and options toolbar -->
        <b-card-footer>
          <b-button-toolbar class="justify-content-center">
            <!-- playback controls -->

            <b-button-group size="sm" class="mx-1">
              <!-- jump to beginning -->
              <b-button variant="outline-dark" @click.stop="jumpToBeginning()">
                <fa-icon icon="fast-backward"></fa-icon>
              </b-button>
            </b-button-group>

            <b-button-group size="sm" class="mx-1">
              <!-- decrease playback speed -->
              <b-button
                variant="outline-dark"
                :disabled="playbackSpeed === -maxPlaybackSpeed"
                @click.stop="decreaseSpeed()"
              >
                <fa-icon icon="backward"></fa-icon>
              </b-button>

              <!-- play/pause -->
              <b-button variant="outline-dark" @click.stop="togglePlayback()">
                <fa-icon :icon="isPlaying ? 'pause' : 'play'"></fa-icon>
              </b-button>

              <!-- increase playback speed -->
              <b-button
                variant="outline-dark"
                :disabled="playbackSpeed === maxPlaybackSpeed"
                @click.stop="increaseSpeed()"
              >
                <fa-icon icon="forward"></fa-icon>
              </b-button>
            </b-button-group>

            <b-button-group size="sm" class="mx-1">
              <!-- jump to end -->
              <b-button variant="outline-dark" @click.stop="jumpToEnd()">
                <fa-icon icon="fast-forward"></fa-icon>
              </b-button>
            </b-button-group>

            <!-- current playback speed -->
            <b-button-group size="sm" class="mx-1">
              <b-button variant="outline-dark" style="width: 46px" disabled>
                {{ playbackSpeed }}x
              </b-button>
            </b-button-group>

            <!-- chart options -->
            <b-button-group size="sm" class="ml-4 mr-0">
              <!-- show the full y-axis (no scaling) -->
              <b-button
                variant="outline-dark"
                :class="{ active: !yScaleAuto }"
                @click.stop="yScaleAuto = false"
              >
                Full Y-Axis
              </b-button>
            </b-button-group>

            <!-- scale the y-axis -->
            <b-button-group size="sm" class="mx-1">
              <!-- turn on  scaling -->
              <b-button
                variant="outline-dark"
                :class="{ active: yScaleAuto }"
                @click.stop="yScaleAuto = true"
              >
                Scale Y-Axis
              </b-button>

              <!-- lock/unlock scaling to the current view -->
              <b-button
                variant="outline-dark"
                :class="{ active: yScaleLocked }"
                :disabled="!yScaleAuto"
                @click.prevent="yScaleLocked = !yScaleLocked"
                ><fa-icon :icon="yScaleLocked ? 'lock' : 'unlock'"></fa-icon
              ></b-button>
            </b-button-group>
          </b-button-toolbar>
        </b-card-footer>
      </b-card>
    </b-overlay>

    <b-overlay :show="downloadingScenario || loadingFailed">
      <template v-slot:overlay><h4></h4></template>

      <!-- buttons to toggle data series and flags -->
      <b-card class="rounded-0">
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
        <b-button
          v-for="(category, i) in logCategoriesWithEntries"
          :key="'toggle-category-' + i"
          variant="light"
          size="sm"
          @click.stop="category.enabled = !category.enabled"
        >
          <fa-icon
            :icon="[category.enabled ? 'fas' : 'far', 'square']"
            :style="{ color: category.color }"
          ></fa-icon>
          {{ category.name }}
        </b-button>
      </b-card>
    </b-overlay>
  </div>
</template>

<script>
import * as d3 from "d3"

import axios from "axios"
import LogFlag from "./LogFlag"

export default {
  name: "Chart",
  components: { LogFlag },
  props: {
    scenario: {
      required: true
    }
  },
  data() {
    return {
      downloadingScenario: true,
      downloadingLogs: true,
      loadingFailed: false,
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
      xAxisNav: null,
      axisWidth: 35,
      axisBufferWidth: 20,
      yScaleAuto: false,
      yScaleLocked: false,
      numTicks: 8,
      hasBackgroundTicks: false,
      axesLoaded: false,
      marginLeft: 0,
      marginRight: 0,
      logCategories: [
        {
          name: "Events",
          color: "#3498db",
          entries: [],
          enabled: true
        },
        {
          name: "Actions",
          color: "#432ec8",
          entries: [],
          enabled: true
        },
        {
          name: "Insults",
          color: "#e74c3c",
          entries: [],
          enabled: true
        },
        {
          name: "Interventions",
          color: "#2ecc71",
          entries: [],
          enabled: true
        }
      ]
    }
  },
  computed: {
    enabledDataSeries() {
      return this.dataSeries.filter(s => s.enabled)
    },
    logCategoriesWithEntries() {
      return this.logCategories.filter(c => c.entries.length)
    },
    numLeftAxes() {
      return this.enabledDataSeries.filter(s => s.yAxisLeft).length
    },
    numRightAxes() {
      return this.enabledDataSeries.filter(s => !s.yAxisLeft).length
    }
  },
  watch: {
    marginLeft() {
      this.updateXScale(this.currentSelectionRange)
    },
    marginRight() {
      this.updateXScale(this.currentSelectionRange)
    },
    enabledDataSeries() {
      this.updateAxes()
    },
    yScaleAuto() {
      this.updateYScale()
      this.updateAxes()
    }
  },
  mounted() {
    this.downloadScenario()
  },
  updated() {
    if (!this.axesLoaded) {
      this.updateAxes()
      this.axesLoaded = true
    }
  },
  methods: {
    downloadScenario() {
      axios
        .get(
          "https://biogearsengine.com/showcase/scenarios/" +
            this.scenario.filename +
            "-datafile.json"
        )
        .then(response => {
          this.downloadingScenario = false
          this.loadData(response.data)
          this.setupBrush()
          this.downloadLog()
        })
        .catch(() => {
          this.loadingFailed = true
        })
    },
    downloadLog() {
      axios
        .get(
          "https://biogearsengine.com/showcase/scenarios/" +
            this.scenario.filename.replace("Results", "") +
            "-log.json"
        )
        .then(response => {
          this.downloadingLogs = false
          this.loadLogs(response.data)
        })
    },
    loadData(jsonData) {
      // find the global min and max values for the x axis
      let xMin = Math.min(...Object.entries(jsonData).map(s => s[1][0][0]))
      let xMax = Math.max(
        ...Object.entries(jsonData).map(s => s[1][s[1].length - 1][0])
      )

      let xDomain = [xMin, xMax]

      // set up the initial scaling for both charts
      if (!this.xScale) {
        this.updateXScale(xDomain)
      }
      if (!this.xScaleNav) {
        this.updateXScaleNav(xDomain)
      }

      let seriesCount = 0
      for (let [key, data] of Object.entries(jsonData)) {
        seriesCount++

        let yDomain = d3.extent(jsonData[key], d => d[1])
        yDomain[0] -= Math.abs(yDomain[1] - yDomain[0]) * this.dataBuffer
        yDomain[1] += Math.abs(yDomain[1] - yDomain[0]) * this.dataBuffer
        let yScale = d3
          .scaleLinear()
          .domain(yDomain)
          .range([this.height - this.margin.bottom, this.margin.top])

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

        // separate the name and the units
        let [name, units] = key.split("(")
        // name = name.replace(/([A-Z])/g, " $1").trim()
        units = units ? units.split(")")[0] : ""

        // add the lines
        // TODO remove any unnecessary values
        this.dataSeries.push({
          key: key,
          name: name,
          index: seriesCount - 1,
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
          yAxisLeft: seriesCount % 2 === 1,
          axisWidth: 0
        })
      }
    },
    loadLogs(logData) {
      for (const category of this.logCategories) {
        if (logData[category.name]) {
          for (const [time, entries] of Object.entries(
            logData[category.name]
          )) {
            let offset = 0
            for (const [eName, eDetails] of Object.entries(entries)) {
              category.entries.push({
                name: eName,
                time: time,
                data: eDetails.data,
                offset: offset
              })
              offset++
            }
          }
        }
      }
    },
    updateXScale(extents) {
      this.xScale = d3
        .scaleLinear()
        .domain(extents)
        .range([this.marginLeft, this.width - this.marginRight])
      this.updateXAxis()
      this.updateEnabledSeries()
    },
    updateXScaleNav(extents) {
      // x scale of nav is static, so keep it separate
      this.xScaleNav = d3
        .scaleLinear()
        .domain(extents)
        .range([this.marginLeft, this.width - this.marginRight])
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
        [this.marginLeft, this.margin.top],
        [this.width - this.marginRight, this.navHeight - this.margin.bottom]
      ])

      // update when the brush moves
      this.brush.on("brush", () => {
        this.currentSelectionRange = d3.event.selection.map(
          this.xScaleNav.invert
        )
        if (d3.event.selection) {
          let newDomain = this.currentSelectionRange
          this.xScale.domain(newDomain)
          this.updateEnabledSeries()
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
    updateEnabledSeries() {
      for (let series of this.enabledDataSeries) {
        this.updateSeries(series)
      }
      if (this.yScaleAuto && !this.yScaleLocked) {
        this.updateAxes()
      }
    },
    updateSeries(series) {
      // filter to only the portion of the line within the visible time frame, keeping any points that are
      // within the visible range, or where the next point before or after is in the visible range
      let newDomain = this.currentSelectionRange

      // find the new min/max using binary search
      let minIndex = this.binarySearch(
        series.data,
        newDomain[0],
        newDomain[1],
        "start"
      )
      let maxIndex = this.binarySearch(
        series.data,
        newDomain[0],
        newDomain[1],
        "end"
      )

      // get just the visible points
      let points
      if (minIndex === -1 || maxIndex === -1) {
        points = []
      } else {
        points = series.data.slice(minIndex, maxIndex + 1)
      }

      // down sample the lines
      points = this.largestTriangleThreeBuckets(
        points,
        Math.round(this.width / this.downscaleFactor)
      )

      if (this.yScaleAuto && !this.yScaleLocked) {
        // get the current y domain of the series and buffer it
        let currentYDomain = d3.extent(points, d => d[1])
        let buffer =
          Math.abs(currentYDomain[1] - currentYDomain[0]) * this.dataBuffer
        if (buffer === 0) {
          buffer = Math.abs(currentYDomain[0] * this.dataBuffer)
        }
        currentYDomain[0] -= buffer
        currentYDomain[1] += buffer

        // set up the new scale and line generator
        let yScale = d3
          .scaleLinear()
          .domain(currentYDomain)
          .range([this.height - this.margin.bottom, this.margin.top])
        series.yScale = yScale
        series.lineGenerator = d3
          .line()
          .x(d => this.xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)
      }

      series.dataPoints = points
      series.line = series.lineGenerator(points)
    },
    updateYScale() {
      for (let series of this.enabledDataSeries) {
        let domain
        if (this.yScaleAuto) {
          // get the current y domain of the series and buffer it
          domain = d3.extent(series.dataPoints, d => d[1])
          let buffer = Math.abs(domain[1] - domain[0]) * this.dataBuffer
          if (buffer === 0) {
            buffer = Math.abs(domain[0] * this.dataBuffer)
          }
          domain[0] -= buffer
          domain[1] += buffer
        } else {
          domain = series.globalYDomain
        }

        // set up the new scale and line generator
        let yScale = d3
          .scaleLinear()
          .domain(domain)
          .range([this.height - this.margin.bottom, this.margin.top])
        series.yScale = yScale
        series.lineGenerator = d3
          .line()
          .x(d => this.xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)

        series.line = series.lineGenerator(series.dataPoints)
      }
    },
    updateAxes() {
      let leftCount = 0
      let rightCount = 0

      this.marginLeft = 6
      this.marginRight = 6

      for (let series of this.enabledDataSeries) {
        // set up the tick marks on the axis
        let tickSize =
          (series.yScale.domain()[1] - series.yScale.domain()[0]) /
          this.numTicks
        let tickValues = [...Array(this.numTicks).keys()].map(
          a => series.yScale.domain()[0] + a * tickSize
        )

        let axis
        if (series.yAxisLeft) {
          // axis is on the left

          axis = d3
            .select(`#ya-${series.index}-${series.name}`)
            .call(d3.axisLeft(series.yScale).tickValues(tickValues))

          // figure out the max label width for spacing the axes
          let maxTextWidth = 0
          axis.selectAll(".tick text").each(function() {
            if (this.getBBox().width > maxTextWidth) {
              maxTextWidth = this.getBBox().width
            }
          })

          // add this axis's width to the left margin so the next axis is positioned correctly
          this.marginLeft += maxTextWidth + this.axisBufferWidth

          // position and color the axis
          axis.attr("transform", `translate(${this.marginLeft}, 0)`)
          leftCount++
          let color = leftCount === this.numLeftAxes ? "#2c3e50" : "none"
          axis.selectAll(".tick line").attr("stroke", color)
          axis.selectAll("path").attr("stroke", color)

          // add the axis data series label
          axis
            .select(`#tl-${series.index}-${series.name}`)
            .attr("transform", "rotate(-90)")
            .attr("y", -maxTextWidth - this.axisBufferWidth - 5)
            .attr("x", -this.height / 2)
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text(series.key)
        } else {
          // axis is on the right

          axis = d3
            .select(`#ya-${series.index}-${series.name}`)
            .call(d3.axisRight(series.yScale).tickValues(tickValues))

          // figure out the max label width for spacing the axes
          let maxTextWidth = 0
          axis.selectAll(".tick text").each(function() {
            if (this.getBBox().width > maxTextWidth) {
              maxTextWidth = this.getBBox().width
            }
          })

          // add this axis's width to the left margin so the next axis is positioned correctly
          this.marginRight += maxTextWidth + this.axisBufferWidth

          // position and color the axis
          axis.attr(
            "transform",
            `translate(${this.width - this.marginRight}, 0)`
          )
          rightCount++
          let color = rightCount === this.numRightAxes ? "#2c3e50" : "none"
          axis.selectAll(".tick line").attr("stroke", color)
          axis.selectAll("path").attr("stroke", color)

          // add the axis data series label
          axis
            .select(`#tl-${series.index}-${series.name}`)
            .attr("transform", "rotate(90)")
            .attr("y", -(maxTextWidth + this.axisBufferWidth + 5))
            .attr("x", this.height / 2)
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text(series.key)
        }

        // color all the text for this axis
        axis.selectAll("text").style("fill", series.color)

        // render the background tick lines if we haven't added any yet
        if (!this.hasBackgroundTicks) {
          axis = d3
            .select("#background-ticks")
            .call(d3.axisRight(series.yScale).tickValues(tickValues))

          axis.selectAll("path").attr("stroke", "none")
          axis.selectAll(".tick text").style("fill", "none")
          axis
            .selectAll(".tick line")
            .attr("stroke", "#2c3e50")
            .attr("stroke-opacity", d => (d === 1 ? null : 0.1))
            .attr("x1", 0)
            .attr("x2", this.width - this.marginLeft - this.marginRight)
            .attr("class", "background-tick")
          this.hasBackgroundTicks = true
        }
      }
    },
    updateTooltip() {
      let min = Infinity

      // get the mouse position
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

        // get the y distance to the two closest point
        // TODO the points can still be outside the margins
        if (!series.dataPoints[i]) {
          yDist = Math.Infinity
        } else {
          yDist = Math.abs(series.yScale(series.dataPoints[i][1]) - ym)
        }

        // select the series whose closest point on the x-axis has the smallest y distance from the mouse
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
    binarySearch(arr, xMin, xMax, mode) {
      let start = 0,
        end = arr.length - 1

      // Iterate while start not meets end
      while (start <= end) {
        // Find the mid index
        let mid = Math.floor((start + end) / 2)

        if (mode === "start") {
          // If this is the element before the first element in the range, or the first element and also within the range
          if (arr[mid][0] < xMin && arr[mid + 1] && arr[mid + 1][0] >= xMin) {
            return mid
          } else if (
            !arr[mid - 1] &&
            arr[mid][0] >= xMin &&
            arr[mid][0] <= xMax
          ) {
            return mid
          }
          // Else look in left or right half accordingly
          else if (arr[mid][0] < xMin) start = mid + 1
          else end = mid - 1
        } else {
          // If element is present at mid, return mid
          if (arr[mid][0] > xMax && arr[mid - 1] && arr[mid - 1][0] <= xMax) {
            return mid
          } else if (
            !arr[mid + 1] &&
            arr[mid][0] <= xMax &&
            arr[mid][0] >= xMin
          ) {
            return mid
          }
          // Else look in left or right half accordingly
          else if (arr[mid][0] < xMax) start = mid + 1
          else end = mid - 1
        }
      }

      return -1
    },
    toMMSS(second) {
      // second = parseInt(second, 10)
      let seconds = second % 60
      if (seconds < 10) {
        seconds = "0" + seconds
      }
      return Math.floor(second / 60) + ":" + seconds
    }
  },
  beforeDestroy() {
    this.stopPlayback()
  }
}
</script>

<style scoped>
.no-rounding > a {
  border-radius: 0;
}
</style>
