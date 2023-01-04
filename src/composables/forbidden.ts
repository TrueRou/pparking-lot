import { Mode, Ruleset } from "./banchoPyMode"

export function forbiddenMode(ruleset: Ruleset, mode: Mode) {
  if (ruleset === "relax" && mode === "mania") return true
  else if (ruleset === "autopilot" && mode !== "osu") return true
  else return false
}

export function forbiddenRuleset(mode: Mode, ruleset: Ruleset) {
  if (mode === "mania" && ruleset === "relax") return true
  else if (mode !== "osu" && ruleset === "autopilot") return true
  else return false
}
