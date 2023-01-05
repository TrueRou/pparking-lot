<script lang="ts">
import axios from "axios";
import { requests } from "@/requests";
import {
  toBanchoPyMode,
  fromBanchoPyMode,
  type Mode,
  type Ruleset,
} from "./composables/banchoPyMode"
import { forbiddenMode, forbiddenRuleset } from "./composables/forbidden";
export default {
  data() {
    return {
      mode: "osu",
      ruleset: "standard",
      filter: "all",
      userId: "",
      tableData: [],
      lastSelect: 4,
      disableMenu: false,
      strainsData: [] as {
        object: number,
        aim: string,
        aim_rx: string,
        aim_delta: string,
        speed: string,
        speed_rx: string,
        speed_delta: string
      }[],
      dialogStrains: false,
      forbiddenMode,
      forbiddenRuleset,
    };
  },
  watch: {
    mode() {
      return this.refresh();
    },
    ruleset() {
      return this.refresh();
    },
    filter() {
      return this.refresh();
    },
    userId() {
      return this.refresh();
    },
  },

  computed: {
    banchoPyMode() {
      if (!this.mode || !this.ruleset) {
        return undefined;
      }

      return toBanchoPyMode(this.mode as Mode, this.ruleset as Ruleset);
    },
    rxForm() {
      return this.ruleset === "relax";
    },
  },

  methods: {
    formatPerformance(obj: Record<string, any>, child: string) {
      return this.getPerformanceSafe(obj, child).toFixed(2);
    },

    getPerformanceSafe(obj: Record<string, any>, child: string) {
      if (obj != null) {
        if (obj.performance_attributes != null) {
          return +obj.performance_attributes[child];
        }
      }
      return 0.0;
    },

    getValueSafe(obj: Record<string, any>) {
      if (obj != null) {
        return obj.toFixed(2);
      }
      return 0.0;
    },

    formatPerformanceVN(obj: Record<string, any>, child: string) {
      return this.getPerformanceSafeVN(obj, child).toFixed(2);
    },

    getPerformanceSafeVN(obj: Record<string, any>, child: string) {
      if (obj != null) {
        if (obj.performance_vn != null) {
          return +obj.performance_vn[child];
        }
      }
      return 0.0;
    },

    sortPPChange<T extends Record<string, any>>(obj1: T, obj2: T) {
      const obj1_change = obj1.performance.new_pp - obj1.performance.old_pp;
      const obj2_change = obj2.performance.new_pp - obj2.performance.old_pp;
      if (obj1_change > obj2_change) return -1;
    },

    sortPerformanceAim<T extends Record<string, any>>(obj1: T, obj2: T) {
      if (
        this.getPerformanceSafe(obj1.performance, "pp_aim") >
        this.getPerformanceSafe(obj2.performance, "pp_aim")
      )
        return -1;
    },

    sortPerformanceAcc<T extends Record<string, any>>(obj1: T, obj2: T) {
      if (
        this.getPerformanceSafe(obj1.performance, "pp_acc") >
        this.getPerformanceSafe(obj2.performance, "pp_acc")
      )
        return -1;
    },

    sortPerformanceSpeed<T extends Record<string, any>>(obj1: T, obj2: T) {
      if (
        this.getPerformanceSafe(obj1.performance, "pp_speed") >
        this.getPerformanceSafe(obj2.performance, "pp_speed")
      )
        return -1;
    },

    sortPerformanceAimVN<T extends Record<string, any>>(obj1: T, obj2: T) {
      if (
        this.getPerformanceSafeVN(obj1.performance, "pp_aim") >
        this.getPerformanceSafeVN(obj2.performance, "pp_aim")
      )
        return -1;
    },

    sortPerformanceSpeedVN<T extends Record<string, any>>(obj1: T, obj2: T) {
      if (
        this.getPerformanceSafeVN(obj1.performance, "pp_speed") >
        this.getPerformanceSafeVN(obj2.performance, "pp_speed")
      )
        return -1;
    },

    async showStrains(score_id: string) {
      this.dialogStrains = true;
      this.strainsData = [];
      const response = await axios.get(
        requests.scores_analysis + "?database_score_id=" + score_id
      );
      // for (let i = 0; i < response.data.aim.length; i++) {
      //   list.push({
      //     object: i + 1,
      //     aim: response.data.aim[i].toFixed(2),
      //     aim_rx: response.data.aim_rx[i].toFixed(2),
      //     aim_delta: Math.abs(response.data.aim_rx[i] - response.data.aim[i]).toFixed(2),
      //     speed: response.data.speed[i].toFixed(2),
      //     speed_rx: response.data.speed_rx[i].toFixed(2),
      //     speed_delta: Math.abs(
      //       response.data.speed_rx[i] - response.data.speed[i]
      //     ).toFixed(2),
      //   });
      // }
      // console.log(list);
      // this.strainsData = list; // avoid too many view updates
      this.strainsData = response.data.aim.map((_: any, i: number) => ({
        object: i + 1,
        aim: response.data.aim[i].toFixed(2),
        aim_rx: response.data.aim_rx[i].toFixed(2),
        aim_delta: Math.abs(response.data.aim_rx[i] - response.data.aim[i]).toFixed(2),
        speed: response.data.speed[i].toFixed(2),
        speed_rx: response.data.speed_rx[i].toFixed(2),
        speed_delta: Math.abs(
          response.data.speed_rx[i] - response.data.speed[i]
        ).toFixed(2),
      }))
    },

    async refresh() {
      if (this.filter === "user" && this.userId) {
        await this.userResults();
      } else if (this.filter === "all") {
        await this.allResults();
      }
    },

    async allResults() {
      const response = await axios.get(requests.scores_mode, {
        params: { mode: this.banchoPyMode },
      });
      this.tableData = response.data;
    },

    async userResults() {
      this.tableData = await axios
        .get(requests.scores_player, {
          params: {
            mode: this.banchoPyMode,
            player_id: this.userId,
          },
        })
        .then((res) => res.data);
    },

    async mounted() {
      this.refresh();
    },
  }
}
</script>

<template>
  <div id="app">
    <el-container style="display: flex; flex-direction: column; min-height: 100vh">
      <el-header class="flush">
        <div style="display: flex; flex-wrap: wrap">
          <el-menu
            :default-active="ruleset"
            @select="(v: Ruleset) => (ruleset = v)"
            class="el-menu-demo"
            mode="horizontal"
            :ellipsis="false"
            ref="header-menu"
          >
            <el-menu-item :disabled="disableMenu" index="standard">standard</el-menu-item>
            <el-menu-item
              :disabled="disableMenu || forbiddenRuleset(mode as Mode, 'relax')"
              index="relax"
              >relax</el-menu-item
            >
            <el-menu-item
              :disabled="disableMenu || forbiddenRuleset(mode as Mode, 'autopilot')"
              index="autopilot"
              >autopilot</el-menu-item
            >
          </el-menu>
          <div
            style="border-bottom: 1px solid var(--el-border-color); flex-grow: 1"
          ></div>
          <el-menu
            :default-active="mode"
            @select="(v: Mode) => (mode = v)"
            mode="horizontal"
            :ellipsis="false"
            ref="header-menu"
          >
            <el-menu-item :disabled="disableMenu" index="osu">osu</el-menu-item>
            <el-menu-item
              :disabled="disableMenu || forbiddenMode(ruleset as Ruleset, 'taiko')"
              index="taiko"
              >taiko</el-menu-item
            >
            <el-menu-item
              :disabled="disableMenu || forbiddenMode(ruleset as Ruleset, 'fruits')"
              index="ctb"
              >ctb</el-menu-item
            >
            <el-menu-item
              :disabled="disableMenu || forbiddenMode(ruleset as Ruleset, 'mania')"
              index="mania"
              >mania</el-menu-item
            >
          </el-menu>
        </div>
      </el-header>
      <el-container class="flex-grow: 1">
        <el-aside width="fit-content">
          <div style="display: flex; flex-direction: column; height: 100%">
            <el-menu
              :default-active="filter"
              @select="(v: 'all' | 'user') => (filter = v)"
              class="el-menu-demo"
              :ellipsis="false"
              ref="header-menu"
            >
              <el-menu-item :disabled="disableMenu" index="all">Show all</el-menu-item>
              <el-menu-item :disabled="disableMenu" index="user">
                <template v-if="filter === 'user'"> Type in user id below </template>
                <template v-else> User </template>
              </el-menu-item>
            </el-menu>
            <template v-if="filter === 'user'">
              <el-input v-model.lazy="userId"></el-input>
              <div class="avatar" v-if="userId">
                <div style="display: flex; justify-content: center; padding: 1em">
                  <el-avatar :size="50" :src="`//a.ppy.sb/${userId}`" />
                </div>
              </div>
            </template>
            <!--            <el-button @click="refresh">Refresh</el-button>-->
          </div>
        </el-aside>
        <el-main style="--el-main-padding: 0">
          <el-table
            :data="tableData"
            style="height: 100%"
            :default-sort="{ prop: 'new_pp', order: 'descending' }"
          >
            <el-table-column header-align="center" label="Score Information">
              <el-table-column prop="beatmap.title" label="Beatmap" fixed width="180">
                <template #default="scope">
                  <el-tooltip
                    effect="dark"
                    :content="'' + scope.row.beatmap.id"
                    placement="top-start"
                  >
                    <div>
                      <el-image
                        style="width: 160px; height: 40px"
                        :src="
                          'https://cdn.sayobot.cn:25225/beatmaps/' +
                          scope.row.beatmap.set_id +
                          '/covers/cover.jpg'
                        "
                        fit="cover"
                      />
                      <div>
                        <span
                          style="
                            font-size: 8px;
                            font-weight: bold;
                            overflow: hidden;
                            white-space: nowrap;
                            text-overflow: ellipsis;
                          "
                        >
                          {{ scope.row.beatmap.title }}
                        </span>
                        <br />
                        <span style="font-size: 4px">{{
                          scope.row.beatmap.version
                        }}</span>
                      </div>
                    </div>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column sortable prop="score.acc" label="Acc" width="80" />
              <el-table-column
                sortable
                prop="score.nmiss"
                label="Miss"
                width="80"
                label-class-name="small-table-column"
              />
              <el-table-column
                sortable
                sort-by="performance.difficulty_attributes.stars"
                label="Stars"
                width="80"
                label-class-name="small-table-column"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    scope.row.performance.difficulty_attributes.stars.toFixed(2)
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column
                sortable
                prop="score.mods_str"
                label="Mods"
                width="120"
                label-class-name="small-table-column"
              />
            </el-table-column>
            <el-table-column header-align="center" label="Performance">
              <el-table-column
                sortable
                prop="performance.old_pp"
                label="Old"
                width="100"
              />
              <el-table-column
                sortable
                prop="performance.new_pp"
                label="New"
                width="100"
              />
              <el-table-column
                sortable
                label="Delta"
                width="120"
                :sort-method="sortPPChange"
              >
                <template #default="scope">
                  <span style="font-size: 14px">
                    {{
                      (
                        scope.row.performance.new_pp - scope.row.performance.old_pp
                      ).toFixed(2)
                    }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column
                v-if="rxForm"
                sort-by="performance.performance_vn.pp"
                label="Vanilla"
                label-class-name="small-table-column"
                sortable
                width="100"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    scope.row.performance.performance_vn.pp.toFixed(2)
                  }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column header-align="center" label="Attributes">
              <el-table-column
                sortable
                label="PPAim"
                width="120"
                :sort-method="sortPerformanceAim"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    formatPerformance(scope.row.performance, "pp_aim")
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column
                sortable
                label="PPAcc"
                width="120"
                :sort-method="sortPerformanceAcc"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    formatPerformance(scope.row.performance, "pp_acc")
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column
                sortable
                label="PPSpd"
                v-if="!rxForm"
                width="120"
                :sort-method="sortPerformanceSpeed"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    formatPerformance(scope.row.performance, "pp_speed")
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column
                sortable
                label="EMC"
                width="120"
                sort-by="performance.performance_attributes.effective_miss_count"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    getValueSafe(
                      scope.row.performance.performance_attributes.effective_miss_count
                    )
                  }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column
              header-align="center"
              v-if="rxForm"
              label="Attributes Vanilla"
            >
              <el-table-column
                v-if="rxForm"
                sortable
                label="PPAim"
                width="120"
                :sort-method="sortPerformanceAimVN"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    formatPerformanceVN(scope.row.performance, "pp_aim")
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column
                v-if="rxForm"
                sortable
                label="PPSpd"
                width="120"
                :sort-method="sortPerformanceSpeedVN"
              >
                <template #default="scope">
                  <span style="font-size: 14px">{{
                    formatPerformanceVN(scope.row.performance, "pp_speed")
                  }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column align="center" label="Action" header-align="center">
              <template #default="scope">
                <el-button @click="showStrains(scope.row.performance.id)"
                  >Analyze Strains</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </el-main>
      </el-container>
    </el-container>
    <el-dialog
      v-if="rxForm"
      width="850"
      v-model="dialogStrains"
      title="Strains"
      style="margin-top: 50px"
    >
      <el-table max-height="720" :data="strainsData">
        <el-table-column sortable property="object" label="No." width="80" />
        <el-table-column header-align="center" label="Aim">
          <el-table-column sortable property="aim" label="Vanilla" width="120" />
          <el-table-column sortable property="aim_rx" label="Relax" width="120" />
          <el-table-column sortable property="aim_delta" label="Delta" width="120" />
        </el-table-column>
        <el-table-column header-align="center" label="Speed">
          <el-table-column sortable property="speed" label="Vanilla" width="120" />
          <el-table-column sortable property="speed_rx" label="Relax" width="120" />
          <el-table-column sortable property="speed_delta" label="Delta" />
        </el-table-column>
      </el-table>
    </el-dialog>
    <el-dialog
      v-if="!rxForm"
      width="360"
      v-model="dialogStrains"
      title="Strains"
      style="margin-top: 50px"
    >
      <el-table max-height="720" :data="strainsData">
        <el-table-column sortable property="object" label="No." width="80" />
        <el-table-column sortable property="aim" label="Aim" width="120" />
        <el-table-column sortable property="speed" label="Speed" />
      </el-table>
    </el-dialog>
  </div>
</template>

<style>
.small-table-column {
  font-size: 8px;
}

body {
  margin: 0;
}

header.el-header.flush {
  padding: 0;
}

/* .el-header {
  position: relative;
  width: 100%;
  height: 70px;
} */

/* .el-main {
  position: absolute;
  left: 0;
  right: 0;
  top: 70px;
  bottom: 0;
  overflow-y: scroll;
} */
</style>
