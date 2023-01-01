<script>
import axios from "axios";
import {requests} from "@/requests";

export default {
  data() {
    return {
      mode: 4,
      user_id: "",
      table_data: [],
      last_select: 4,
      disable_menu: false,
      rx_form: true,
    }
  },

  methods: {
    formatPerformance(obj, child) {
      return this.getPerformanceSafe(obj, child).toFixed(2)
    },

    getPerformanceSafe(obj, child) {
      if (obj != null) {
        if (obj.performance_attributes != null) {
          return +obj.performance_attributes[child]
        }
      }
      return 0.0
    },

    formatPerformanceVN(obj, child) {
      return this.getPerformanceSafeVN(obj, child).toFixed(2)
    },

    getPerformanceSafeVN(obj, child) {
      if (obj != null) {
        if (obj.performance_vn != null) {
          return +obj.performance_vn[child]
        }
      }
      return 0.0
    },

    sortPPChange(obj1, obj2) {
      const obj1_change = obj1.performance.new_pp - obj1.performance.old_pp
      const obj2_change = obj2.performance.new_pp - obj2.performance.old_pp
      if (obj1_change > obj2_change) return -1
    },

    sortPerformanceAim(obj1, obj2) {
      if (this.getPerformanceSafe(obj1.performance, "pp_aim") > this.getPerformanceSafe(obj2.performance, "pp_aim")) return -1
    },

    sortPerformanceAcc(obj1, obj2) {
      if (this.getPerformanceSafe(obj1.performance, "pp_acc") > this.getPerformanceSafe(obj2.performance, "pp_acc")) return -1
    },

    sortPerformanceSpeed(obj1, obj2) {
      if (this.getPerformanceSafe(obj1.performance, "pp_speed") > this.getPerformanceSafe(obj2.performance, "pp_speed")) return -1
    },

    sortPerformanceAimVN(obj1, obj2) {
      if (this.getPerformanceSafeVN(obj1.performance, "pp_aim") > this.getPerformanceSafeVN(obj2.performance, "pp_aim")) return -1
    },

    sortPerformanceSpeedVN(obj1, obj2) {
      if (this.getPerformanceSafeVN(obj1.performance, "pp_speed") > this.getPerformanceSafeVN(obj2.performance, "pp_speed")) return -1
    },

    async handleSelect(key, keyPath) {
      if (+key === 10) {
        this.user_id = +window.prompt("请输入玩家ID","");
        const response = await axios.get(requests.scores_player + "?mode=" + this.last_select + "&player_id=" + this.user_id)
        this.rx_form = +this.last_select === 4
        this.table_data = response.data
        return
      }
      else if (+key === 11) {
        this.disable_menu = true
        if (this.user_id !== "") {
          await axios.patch(requests.scores_player + "?mode=" + this.last_select + "&player_id=" + this.user_id)
        } else {
          await axios.patch(requests.scores_mode + "?mode=" + this.last_select)
        }
        location.reload();
        return
      }
      const response = await axios.get(requests.scores_mode + "?mode=" + key)
      this.rx_form = +key === 4
      this.table_data = response.data
      this.last_select = key
    }
  },

  async mounted() {
    const response = await axios.get(requests.scores_mode + "?mode=" + this.mode)
    this.table_data = response.data
  }
}

</script>

<template>
  <div id="app">
    <el-container>
      <el-header>
        <el-menu
            default-active="4"
            class="el-menu-demo"
            mode="horizontal"
            :ellipsis="false"
            @select="handleSelect"
            ref="header-menu"
        >

          <el-menu-item :disabled="disable_menu" index="0">stard-vn</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="4">stard-rx</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="8">stard-ap</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="1">taiko-vn</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="5">taiko-rx</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="2">catch-vn</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="6">catch-rx</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="3">mania-vn</el-menu-item>

          <div style="flex-grow: 1;" />
          <el-menu-item :disabled="disable_menu" index="10">{{ user_id || "筛选玩家" }}</el-menu-item>
          <el-menu-item :disabled="disable_menu" index="11">更新数据</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <el-table :data="table_data" border style="width: 100%; height: 100%" :default-sort="{ prop: 'new_pp', order: 'descending' }">
          <el-table-column header-align="center" label="Score Information">
            <el-table-column prop="beatmap.title" label="Beatmap" fixed width="180">
              <template #default="scope">
                <el-tooltip
                    effect="dark"
                    :content="'' + scope.row.beatmap.id"
                    placement="top-start"
                >
                  <div>
                    <el-image style="width: 160px; height: 40px;" :src="'https://cdn.sayobot.cn:25225/beatmaps/'+ scope.row.beatmap.set_id +'/covers/cover.jpg'" fit="cover" />
                    <div>
                      <span style="font-size: 8px; font-weight: bold; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">{{ scope.row.beatmap.title }}</span><br>
                      <span style="font-size: 4px;">{{ scope.row.beatmap.version }}</span>
                    </div>
                  </div>
                </el-tooltip>

              </template>
            </el-table-column>
            <el-table-column sortable prop="score.acc" label="Acc" width="80"/>
            <el-table-column sortable prop="score.nmiss" label="Miss" width="80" label-class-name="small-table-column"/>
            <el-table-column sortable sort-by="performance.difficulty_attributes.stars" label="Stars" width="80" label-class-name="small-table-column">
              <template #default="scope">
                <span style="font-size: 14px;">{{ scope.row.performance.difficulty_attributes.stars.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column sortable prop="score.mods_str" label="Mods" width="120" label-class-name="small-table-column"/>
          </el-table-column>
          <el-table-column header-align="center" label="Performance">
            <el-table-column sortable prop="performance.old_pp" label="Old" width="100"/>
            <el-table-column sortable prop="performance.new_pp" label="New" width="100"/>
            <el-table-column sortable label="Delta" width="120" :sort-method="sortPPChange">
              <template #default="scope">
                <span style="font-size: 14px;">{{ (scope.row.performance.new_pp - scope.row.performance.old_pp).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column v-if="rx_form" sort-by="performance.performance_vn.pp" label="Vanilla" label-class-name="small-table-column" sortable width="100">
              <template #default="scope">
                <span style="font-size: 14px;">{{ scope.row.performance.performance_vn.pp.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table-column>
          <el-table-column header-align="center" label="Attributes">
            <el-table-column sortable label="PPAim" width="120" :sort-method="sortPerformanceAim">
              <template #default="scope">
                <span style="font-size: 14px;">{{ formatPerformance(scope.row.performance, "pp_aim") }}</span>
              </template>
            </el-table-column>
            <el-table-column  sortable label="PPAcc" width="120" :sort-method="sortPerformanceAcc">
              <template #default="scope">
                <span style="font-size: 14px;">{{ formatPerformance(scope.row.performance, "pp_acc") }}</span>
              </template>
            </el-table-column>
            <el-table-column sortable label="PPSpd" width="120" :sort-method="sortPerformanceSpeed">
              <template #default="scope">
                <span style="font-size: 14px;">{{ formatPerformance(scope.row.performance, "pp_speed") }}</span>
              </template>
            </el-table-column>
            <el-table-column sortable label="EMC" width="120" sort-by="performance.performance_attributes.effective_miss_count">
              <template #default="scope">
                <span style="font-size: 14px;">{{ scope.row.performance.performance_attributes.effective_miss_count.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table-column>
          <el-table-column header-align="center" v-if="rx_form" label="Attributes Vanilla">
            <el-table-column v-if="rx_form" sortable label="PPAim" width="120" :sort-method="sortPerformanceAimVN">
              <template #default="scope">
                <span style="font-size: 14px;">{{ formatPerformanceVN(scope.row.performance, "pp_aim") }}</span>
              </template>
            </el-table-column>
            <el-table-column v-if="rx_form" sortable label="PPSpd" width="120" :sort-method="sortPerformanceSpeedVN">
              <template #default="scope">
                <span style="font-size: 14px;">{{ formatPerformanceVN(scope.row.performance, "pp_speed") }}</span>
              </template>
            </el-table-column>
          </el-table-column>
          <el-table-column align="center" label="Action" header-align="center">
            <template #default="scope">
              <el-button>Analyze Strains</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-main>
    </el-container>
  </div>
</template>

<style>
.small-table-column {
  font-size: 8px;
}

.el-header {
  position: relative;
  width: 100%;
  height: 70px;
}

.el-main {
  position: absolute;
  left: 0;
  right: 0;
  top: 70px;
  bottom: 0;
  overflow-y: scroll;
}

</style>
