import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import * as api from "../api.js";

// Build the editable condition state from a scenario's defaults.
function initConditions(sc) {
  const v = Object.fromEntries(sc.victory_conditions.map((c) => [c.type, c]));
  const f = Object.fromEntries(sc.failure_conditions.map((c) => [c.type, c]));
  return {
    victory: {
      survive_rounds: {
        on: "survive_rounds" in v,
        rounds: v.survive_rounds?.rounds ?? sc.rounds,
      },
      enemy_pressure_zero: { on: "enemy_pressure_zero" in v },
    },
    failure: {
      morale_zero: { on: "morale_zero" in f },
      political_pressure_max: { on: "political_pressure_max" in f },
      supply_zero: { on: "supply_zero" in f },
      enemy_controls_zones: {
        on: "enemy_controls_zones" in f,
        count: f.enemy_controls_zones?.count ?? 3,
      },
      core_zones_lost: {
        on: "core_zones_lost" in f,
        core_zones:
          f.core_zones_lost?.core_zones ??
          sc.zones.filter((z) => z.core).map((z) => z.code),
      },
    },
  };
}

function buildPayload(file, cond) {
  const victory = [];
  if (cond.victory.survive_rounds.on)
    victory.push({ type: "survive_rounds", rounds: cond.victory.survive_rounds.rounds });
  if (cond.victory.enemy_pressure_zero.on)
    victory.push({ type: "enemy_pressure_zero" });

  const failure = [];
  if (cond.failure.morale_zero.on) failure.push({ type: "morale_zero" });
  if (cond.failure.political_pressure_max.on)
    failure.push({ type: "political_pressure_max" });
  if (cond.failure.supply_zero.on) failure.push({ type: "supply_zero" });
  if (cond.failure.enemy_controls_zones.on)
    failure.push({
      type: "enemy_controls_zones",
      count: cond.failure.enemy_controls_zones.count,
    });
  if (cond.failure.core_zones_lost.on)
    failure.push({
      type: "core_zones_lost",
      core_zones: cond.failure.core_zones_lost.core_zones,
    });

  return { scenario: file, victory_conditions: victory, failure_conditions: failure };
}

function Toggle({ checked, onChange, children }) {
  return (
    <label className={`cond ${checked ? "on" : ""}`}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{children}</span>
    </label>
  );
}

export default function SetupScreen({ onStart, busy }) {
  const [scenarios, setScenarios] = useState(null);
  const [selected, setSelected] = useState(null); // scenario file name
  const [cond, setCond] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listScenarios()
      .then((list) => {
        setScenarios(list);
        if (list.length) {
          setSelected(list[0].file);
          setCond(initConditions(list[0]));
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  const scenario = useMemo(
    () => scenarios?.find((s) => s.file === selected) ?? null,
    [scenarios, selected]
  );

  const pick = (sc) => {
    setSelected(sc.file);
    setCond(initConditions(sc));
  };

  const setVictory = (key, patch) =>
    setCond((c) => ({
      ...c,
      victory: { ...c.victory, [key]: { ...c.victory[key], ...patch } },
    }));
  const setFailure = (key, patch) =>
    setCond((c) => ({
      ...c,
      failure: { ...c.failure, [key]: { ...c.failure[key], ...patch } },
    }));

  const victoryCount = cond
    ? Object.values(cond.victory).filter((x) => x.on).length
    : 0;
  const failureCount = cond
    ? Object.values(cond.failure).filter((x) => x.on).length
    : 0;
  const ready = scenario && cond && victoryCount >= 1 && failureCount >= 1;

  if (!scenarios) {
    return (
      <div className="setup">
        <div className="setup-box loading">{error || "正在載入劇本…"}</div>
      </div>
    );
  }

  return (
    <div className="setup">
      <motion.div
        className="setup-box"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 160, damping: 20 }}
      >
        <div className="setup-head">
          <h1>決戰20</h1>
          <span className="sub">作戰準備 — 選擇戰場並設定勝負條件</span>
        </div>

        <h3 className="setup-label">① 選擇作戰劇本</h3>
        <div className="scenario-grid">
          {scenarios.map((sc) => (
            <motion.button
              key={sc.file}
              className={`scenario-card ${sc.file === selected ? "active" : ""}`}
              onClick={() => pick(sc)}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="sc-name">{sc.name}</div>
              <div className="sc-meta">
                {sc.rounds} 回合 ・ {sc.zones.length} 防區 ・ {sc.forces.length} 支部隊
              </div>
              <div className="sc-zones">
                {sc.zones.map((z) => (
                  <span key={z.code} className={`sc-zone ${z.core ? "core" : ""}`}>
                    {z.core ? "★" : ""}{z.name}
                  </span>
                ))}
              </div>
            </motion.button>
          ))}
        </div>

        {scenario && scenario.briefing && (
          <div className="briefing">
            <div className="briefing-tag">機密 ── 作戰簡報</div>
            {scenario.briefing}
          </div>
        )}

        {cond && (
          <div className="cond-grid">
            <div>
              <h3 className="setup-label">② 勝利條件（至少一項）</h3>
              <Toggle
                checked={cond.victory.survive_rounds.on}
                onChange={(on) => setVictory("survive_rounds", { on })}
              >
                堅守
                <input
                  type="number"
                  className="num"
                  min={5}
                  max={scenario.rounds}
                  value={cond.victory.survive_rounds.rounds}
                  disabled={!cond.victory.survive_rounds.on}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) =>
                    setVictory("survive_rounds", {
                      rounds: Math.max(5, Math.min(scenario.rounds, Number(e.target.value) || 5)),
                    })
                  }
                />
                回合
              </Toggle>
              <Toggle
                checked={cond.victory.enemy_pressure_zero.on}
                onChange={(on) => setVictory("enemy_pressure_zero", { on })}
              >
                將敵軍壓力壓制歸零
              </Toggle>
            </div>
            <div>
              <h3 className="setup-label">③ 失敗條件（至少一項）</h3>
              <Toggle
                checked={cond.failure.morale_zero.on}
                onChange={(on) => setFailure("morale_zero", { on })}
              >
                士氣歸零即潰敗
              </Toggle>
              <Toggle
                checked={cond.failure.political_pressure_max.on}
                onChange={(on) => setFailure("political_pressure_max", { on })}
              >
                政治壓力達 100 即下台
              </Toggle>
              <Toggle
                checked={cond.failure.supply_zero.on}
                onChange={(on) => setFailure("supply_zero", { on })}
              >
                補給耗盡即斷糧
              </Toggle>
              <Toggle
                checked={cond.failure.enemy_controls_zones.on}
                onChange={(on) => setFailure("enemy_controls_zones", { on })}
              >
                敵軍控制
                <input
                  type="number"
                  className="num"
                  min={1}
                  max={scenario.zones.length}
                  value={cond.failure.enemy_controls_zones.count}
                  disabled={!cond.failure.enemy_controls_zones.on}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) =>
                    setFailure("enemy_controls_zones", {
                      count: Math.max(1, Math.min(scenario.zones.length, Number(e.target.value) || 1)),
                    })
                  }
                />
                個防區即潰敗
              </Toggle>
              <Toggle
                checked={cond.failure.core_zones_lost.on}
                onChange={(on) => setFailure("core_zones_lost", { on })}
              >
                ★核心防區全數失守即潰敗
              </Toggle>
            </div>
          </div>
        )}

        <div className="setup-foot">
          {!ready && cond && (
            <span className="setup-warn">勝利與失敗條件須各至少勾選一項。</span>
          )}
          <motion.button
            className="start-btn"
            disabled={!ready || busy}
            onClick={() => onStart(buildPayload(selected, cond))}
            whileHover={ready && !busy ? { scale: 1.04 } : undefined}
            whileTap={ready && !busy ? { scale: 0.96 } : undefined}
          >
            ▶ 開始作戰
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
