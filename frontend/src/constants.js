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
