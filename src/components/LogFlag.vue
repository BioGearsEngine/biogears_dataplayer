<template>
  <g
    :id="'flag-' + category.name + '-' + index"
    :transform="'translate(' + xPos + ', ' + entry.offset * 26 + ')'"
    data-container="body"
    cursor="default"
    @mouseenter="flag.raise()"
  >
    <g
      :id="'flag-rect-' + category.name + '-' + index"
      v-b-popover.hover.bottom.noninteractive.html="entryData"
    >
      <rect :fill="category.color" :width="textWidth" height="1.5rem"></rect>
    </g>
    <line
      x1="0"
      x2="0"
      y1="0"
      :y2="height"
      :stroke="category.color"
      stroke-width="1"
    ></line>
  </g>
</template>

<script>
import * as d3 from "d3"

export default {
  name: "LogFlag",
  props: {
    xPos: {
      required: true
    },
    height: {
      required: true
    },
    category: {
      required: true
    },
    entry: {
      required: true
    },
    index: {
      required: true
    }
  },
  data() {
    return {
      group: null,
      flag: null,
      margin: 10,
      textWidth: 0
    }
  },
  computed: {
    entryData() {
      if (this.entry.data !== undefined) {
        let text = ""
        for (let dataEntry of this.entry.data) {
          text +=
            dataEntry.label + ": <strong>" + dataEntry.value + "</strong></br>"
        }
        return text
      } else return null
    }
  },
  mounted() {
    let self = this

    this.flag = d3.select("#flag-" + this.category.name + "-" + this.index)
    this.rect = d3.select("#flag-rect-" + this.category.name + "-" + this.index)

    // append the text when mounting so we can size the rectangle to the text width
    this.rect
      .append("text")
      .text(this.entry.name)
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
      .attr("x", this.margin)
      .attr("y", "1rem")
      .attr("fill", "white")

    this.rect.selectAll("text").each(function() {
      self.textWidth = this.getBBox().width + self.margin * 2
    })
  }
}
</script>

<style scoped></style>
