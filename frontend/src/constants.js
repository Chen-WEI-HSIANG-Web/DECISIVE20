export const STATUS_LABEL = {
  friendly: "我方控制",
  contested: "爭奪中",
  enemy_controlled: "敵方控制",
  cut_off: "被切斷",
  destroyed: "已破壞",
};

export const STATUS_VAR = {
  friendly: "var(--green)",
  contested: "var(--yellow)",
  enemy_controlled: "var(--red)",
  cut_off: "var(--magenta)",
  destroyed: "var(--grey)",
};

export const ENDING_LABEL = {
  victory: "勝利",
  failure: "失敗",
  incomplete: "未分勝負",
};

export const ENDING_VAR = {
  victory: "var(--green)",
  failure: "var(--red)",
  incomplete: "var(--yellow)",
};

// label, key, max, danger(value) -> bool, warn(value) -> bool
export const RES_DEF = [
  ["補給 Supply", "supply", 20, (v) => v <= 2, (v) => v / 20 < 0.35],
  ["情報 Intel", "intel", 20, () => false, () => false],
  ["士氣 Morale", "morale", 100, (v) => v < 20, (v) => v < 35],
  ["政治壓力 Pressure", "political_pressure", 100, (v) => v > 80, (v) => v > 65],
  ["敵軍壓力 Enemy", "enemy_pressure", 40, (v) => v >= 24, (v) => v >= 16],
];

const RES_LABEL = {
  supply: "補給",
  intel: "情報",
  morale: "士氣",
  political_pressure: "政治壓力",
  enemy_pressure: "敵軍壓力",
  cp: "指令點",
};

const signed = (v) => (v >= 0 ? `+${v}` : `${v}`);

// Turn an option's effects object into display chips. `good` drives the colour:
// for pressures, a decrease is the good outcome; for everything else, an increase.
export function formatEffects(effects) {
  const chips = [];
  for (const [key, value] of Object.entries(effects || {})) {
    if (key === "zone_defense") {
      for (const [zone, d] of Object.entries(value))
        chips.push({ text: `${zone} 防禦 ${signed(d)}`, good: d >= 0 });
    } else if (key === "zone_status") {
      for (const [zone, status] of Object.entries(value))
        chips.push({
          text: `${zone} → ${STATUS_LABEL[status] || status}`,
          good: status === "friendly",
        });
    } else if (key === "force_value") {
      for (const [name, d] of Object.entries(value))
        chips.push({ text: `${name} ${signed(d)}`, good: d >= 0 });
    } else {
      const pressure = key === "political_pressure" || key === "enemy_pressure";
      chips.push({
        text: `${RES_LABEL[key] || key} ${signed(value)}`,
        good: pressure ? value < 0 : value >= 0,
      });
    }
  }
  return chips;
}
