import Vue from "vue"
import App from "./App.vue"

import { BootstrapVue } from "bootstrap-vue"
import "./scss/custom.scss"

import { library } from "@fortawesome/fontawesome-svg-core"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import {
  faCircle,
  faFastBackward,
  faBackward,
  faPlay,
  faPause,
  faForward,
  faFastForward,
  faLock,
  faUnlock
} from "@fortawesome/free-solid-svg-icons"
import { faCircle as faCircleRegular } from "@fortawesome/free-regular-svg-icons"

library.add(
  faCircle,
  faFastBackward,
  faBackward,
  faPlay,
  faPause,
  faForward,
  faFastForward,
  faCircleRegular,
  faLock,
  faUnlock
)
Vue.component("fa-icon", FontAwesomeIcon)

Vue.use(BootstrapVue)

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount("#app")
