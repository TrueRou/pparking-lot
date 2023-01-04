export const mode = ['osu', 'taiko', 'fruits', 'mania'] as const
export type Mode = typeof mode[number]

export const ruleset = ['standard', 'relax', 'autopilot'] as const
export type Ruleset = typeof ruleset[number]

export enum BanchoPyMode {
  osuStandard = 0,
  taikoStandard = 1,
  fruitsStandard = 2,
  maniaStandard = 3,

  osuRelax = 4,
  taikoRelax = 5,
  fruitsRelax = 6,
  // maniaRelax = 7,

  osuAutopilot = 8,
  // taikoAutopilot = 9,
  // fruitsAutopilot = 10,
  // maniaAutopilot = 11,
}

export function capitalizeFirstLetter<T extends string>(string: T) {
  return (string.charAt(0).toUpperCase() + string.slice(1)) as Capitalize<T>
}


export function toBanchoPyMode(mode: Mode, ruleset: Ruleset): BanchoPyMode | undefined {
  const joined: `${Mode}${Capitalize<Ruleset>}` = `${mode}${capitalizeFirstLetter(ruleset)}`
  switch (joined) {
    case 'maniaRelax':
    case 'taikoAutopilot':
    case 'fruitsAutopilot':
    case 'maniaAutopilot':
      return
    default:
      return BanchoPyMode[joined]
  }
}


const reverseRuleset: Record<number, Ruleset> = {
  0: 'standard',
  1: 'relax',
  2: 'autopilot',
}
const reverseMode: Record<number, Mode> = {
  0: 'osu',
  1: 'taiko',
  2: 'fruits',
  3: 'mania',
}

export function fromBanchoPyMode(input: BanchoPyMode): [Mode, Ruleset] {
  const modeKey = input % 4
  const rulesetKet = Math.floor(input / 4)

  return [reverseMode[modeKey], reverseRuleset[rulesetKet]]
}