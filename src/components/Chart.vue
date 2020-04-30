<template>
  <div>
    <h1>Actual Data Test</h1>
    <!--    <div id="line-chart" style="width: 954px; margin: auto" />-->
    <svg
      id="line-chart"
      :width="width"
      :height="height"
      style="background: #eeeeee"
    >
      <path
        v-for="(line, index) in lines"
        :key="'l-' + index"
        :d="line"
        fill="none"
        opacity="0.85"
        :stroke="colors[index]"
        stroke-width="1.5"
        stroke-miterlimit="1"
        class="line"
      />
    </svg>
    <br />
    <svg
      id="nav-bar"
      :width="width"
      :height="navHeight"
      style="background: #eeeeee"
    >
      <path
        v-for="(line, index) in navLines"
        :key="'nl-' + index"
        :d="line"
        fill="none"
        opacity="0.75"
        :stroke="colors[index]"
        stroke-width="1"
        stroke-miterlimit="1"
        class="nav-line"
      />
      <g id="brush" />
    </svg>
  </div>
</template>

<script>
import * as d3 from "d3"

// import { SEPSIS_JSON as DATAFILE } from "../static/sepsis-datafile"
// import { EXPOSURE_JSON as DATAFILE } from "../static/exposure-datafile"
import { ASTHMA_JSON as DATAFILE } from "../static/asthma-datafile"

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
      lineData: "",
      colors: [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf"
      ]
    }
  },
  mounted() {
    this.drawCharts()
  },
  methods: {
    drawCharts() {
      let jsonData = JSON.parse(DATAFILE)
      const keys = Object.keys(jsonData)

      // TODO may need to check for actual min/max
      let xScale = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[keys[0]], d => d[0]))
        .range([this.margin.left, this.width - this.margin.right])

      // xScale will change, so keep the xScale for the nav separate
      let xScaleNav = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[keys[0]], d => d[0]))
        .range([this.margin.left, this.width - this.margin.right])

      let yScales = []
      let yNavScales = []
      let navLineGenerators = []
      let lineGenerators = []
      for (let key of keys) {
        // set up each lines yScale for the full chart
        let yScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.height - this.margin.bottom, this.margin.top])
        yScales.push(yScale)
        // set up each lines generator for the full chart
        let lineGenerator = d3
          .line()
          .x(d => xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)
        lineGenerators.push(lineGenerator)
        // add the lines
        this.lines.push(lineGenerator(jsonData[key]))

        // TODO for now just add one line
        // if (this.navLines.length < 1) {
        console.log("Nav line has " + jsonData[key].length + " points")
        // set up each lines yScale for the nav chart
        let yNavScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.navHeight - this.margin.bottom, this.margin.top])
        yNavScales.push(yNavScale)
        // set up each lines generator for the nav chart
        let navLineGenerator = d3
          .line()
          .x(d => xScaleNav(d[0]))
          .y(d => yNavScale(d[1]))
          .curve(d3.curveMonotoneX)
        navLineGenerators.push(navLineGenerator)

        // downscale the nav lines further than the main chart
        let points = this.largestTriangleThreeBuckets(
          jsonData[key],
          this.width / 2
        )
        console.log("Nav line reduce to " + points.length + " points")
        this.navLines.push(navLineGenerator(points))
        // this.navLines.push(navLineGenerator(jsonData[key]))
      }
      // }

      // set up the brush
      const brush = d3.brushX().extent([
        [this.margin.left, this.margin.top],
        [this.width - this.margin.right, this.navHeight - this.margin.bottom]
      ])

      brush.on("brush", () => {
        // let start = window.performance.now()
        this.lines = []
        if (d3.event.selection) {
          let newDomain = d3.event.selection.map(xScaleNav.invert)
          xScale.domain(newDomain)
          for (let [index, key] of keys.entries()) {
            // filter to only the portion of the line within the visible time frame
            let points = jsonData[key]
            // TODO update the filtering to keep one point outside the range
            points = points.filter(
              a => a[0] >= newDomain[0] - 1 && a[0] <= newDomain[1] + 1
            )
            // downscale the lines
            points = this.largestTriangleThreeBuckets(
              points,
              Math.round(this.width / 4)
            )
            this.lines.push(lineGenerators[index](points))
          }
        }
        // let end = window.performance.now()
        // console.log("time for brush update: " + (end - start))
      })

      let beforeBrushStarted = function() {
        // Use a fixed width when re-centering
        // TODO update to use the current width if set
        const dx = xScaleNav(60) - xScaleNav(0)
        const [cx] = d3.mouse(this)
        const [x0, x1] = [cx - dx / 2, cx + dx / 2]
        const [X0, X1] = xScaleNav.range()
        d3.select(this.parentNode).call(
          brush.move,
          x1 > X1 ? [X1 - dx, X1] : x0 < X0 ? [X0, X0 + dx] : [x0, x1]
        )
      }

      const g = d3.select("#brush")
      g.call(brush)
        .call(brush.move, [0, 60].map(xScaleNav))
        .call(g =>
          g
            .select(".overlay")
            .datum({ type: "selection" })
            .on("mousedown touchstart", beforeBrushStarted)
        )
    },
    startPlaying() {
      setInterval(() => {}, 100)
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
    // testing creating a chart with real data
    loadFromJson() {
      // prepare the data
      let jsonData = JSON.parse(DATAFILE)
      const keys = Object.keys(jsonData)

      let xScale = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[keys[0]], d => d[0]))
        // .domain([0, 60])
        .range([this.margin.left, this.width - this.margin.right])

      // add the lines
      let totalPoints = 0
      for (const key of keys) {
        xScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[0]))
          .range([this.margin.left, this.width - this.margin.right])

        let yScale = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.height - this.margin.bottom, this.margin.top])

        let line = d3
          .line()
          .x(d => xScale(d[0]))
          .y(d => yScale(d[1]))
          .curve(d3.curveMonotoneX)

        this.lines.push(line(jsonData[key]))

        console.log("length of " + key + " data: " + jsonData[key].length)
        totalPoints += jsonData[key].length
      }
      console.log("Total points: " + totalPoints)

      let xScaleNav = d3
        .scaleLinear()
        .domain(d3.extent(jsonData[keys[0]], d => d[0]))
        .range([this.margin.left, this.width - this.margin.right])

      for (const key of keys) {
        // create the nav bar

        let yScaleNav = d3
          .scaleLinear()
          .domain(d3.extent(jsonData[key], d => d[1]))
          .range([this.navHeight - this.margin.bottom, this.margin.top])

        // TODO add the xAxis tick marks
        // let xAxis = g =>
        //   g
        //     .attr(
        //       "transform",
        //       `translate(0,${this.height - this.lineChartMargin.bottom})`
        //     )
        //     .call(
        //       d3
        //         .axisBottom(xScale)
        //         .ticks(this.width / 80)
        //         .tickSizeOuter(0)co
        //     )

        let line = d3
          .line()
          .x(d => xScaleNav(d[0]))
          .y(d => yScaleNav(d[1]))
          .curve(d3.curveMonotoneX)

        this.navLines.push(line(jsonData[key]))
        break
      }

      const brush = d3.brushX().extent([
        [this.margin.left, this.margin.top],
        [this.width - this.margin.right, this.navHeight - this.margin.bottom]
      ])

      // TODO this works, but it's slow...
      brush.on("brush", () => {
        let start = window.performance.now()
        if (d3.event.selection) {
          let newDomain = d3.event.selection.map(xScaleNav.invert)
          xScale.domain(newDomain)

          this.lines = []
          for (const key of keys) {
            let yScale = d3
              .scaleLinear()
              .domain(d3.extent(jsonData[key], d => d[1]))
              .range([this.height - this.margin.bottom, this.margin.top])
            let line = d3
              .line()
              .x(d => xScale(d[0]))
              .y(d => yScale(d[1]))
              .curve(d3.curveMonotoneX)
            this.lines.push(line(jsonData[key]))
            // break
          }
        }
        let end = window.performance.now()
        console.log("time for brush update: " + (start - end))
      })

      // Use a fixed width when re-centering.
      let beforeBrushStarted = function() {
        const dx = xScaleNav(600) - xScaleNav(0)
        const [cx] = d3.mouse(this)
        const [x0, x1] = [cx - dx / 2, cx + dx / 2]
        const [X0, X1] = xScaleNav.range()
        d3.select(this.parentNode).call(
          brush.move,
          x1 > X1 ? [X1 - dx, X1] : x0 < X0 ? [X0, X0 + dx] : [x0, x1]
        )
      }

      const g = d3.select("#brush")
      g.call(brush)
        .call(brush.move, [0, 10].map(xScaleNav))
        .call(
          g =>
            g
              .select(".overlay")
              .datum({ type: "selection" })
              .on("mousedown touchstart", beforeBrushStarted)
          // .on("mousedown touchstart", () => console.log("brushStarted"))
        )

      // // test out a sample zoom function
      // const zoom = d3
      //   .zoom()
      //   .scaleExtent([1, 32])
      //   .extent([
      //     [this.margin.left, 0],
      //     [this.width - this.margin.right, this.height]
      //   ])
      //   .translateExtent([
      //     [this.margin.left, -Infinity],
      //     [this.width - this.margin.right, Infinity]
      //   ])
      //   .on("zoom", () => {
      //     let l = d3.selectAll("path").filter(".line")
      //     l.attr("transform", d3.event.transform)
      //   })
      //
      // d3.select("#line-chart")
      //   .call(zoom)
      //   .transition()
      //   .duration(750)
      //   .call(zoom.scaleTo, 4, [xScale(0), xScale(60)])
    }
  }
}
</script>

<style scoped />
