import { motion, AnimatePresence } from "framer-motion";
import { STATUS_LABEL, STATUS_VAR } from "../constants.js";

function Zone({ zone, clickable, flashed, targeted, onPick }) {
  const dpct = Math.max(0, Math.min(100, (zone.defense / 10) * 100));
  return (
    <motion.li
      layout
      className={`zone ${clickable ? "clickable" : ""} ${targeted ? "targeted" : ""}`}
      style={{ borderLeftColor: STATUS_VAR[zone.status] }}
      animate={{ borderLeftColor: STATUS_VAR[zone.status] }}
      onClick={clickable ? () => onPick(zone.code) : undefined}
      whileHover={clickable ? { scale: 1.02, x: 3 } : undefined}
    >
      {targeted && <div className="threat" title="敵軍預定攻擊">⚠</div>}
      <AnimatePresence>
        {flashed && (
          <motion.div
            className="zone-flash"
            initial={{ opacity: 0.85 }}
            animate={{ opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.9 }}
            style={{ backgroundColor: STATUS_VAR[zone.status] }}
          />
        )}
      </AnimatePresence>
      <div className="code">{zone.code}</div>
      <div className="name">
        {zone.name}
        {zone.core && <span className="core">★核心</span>}
      </div>
      <div className="dwrap">
        <div className="dbar">
          <motion.span
            animate={{ width: `${dpct}%` }}
            transition={{ type: "spring", stiffness: 140, damping: 18 }}
          />
        </div>
        <div className="dlabel">防禦 {zone.defense}</div>
      </div>
      <motion.div
        className="status"
        key={zone.status}
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0, color: STATUS_VAR[zone.status] }}
      >
        {STATUS_LABEL[zone.status] || zone.status}
      </motion.div>
    </motion.li>
  );
}

export default function ZoneMap({ state, pending, flash, onPick }) {
  const targeted = new Set(state.predicted_attacks || []);
  return (
    <section className="panel">
      <h2>防區地圖</h2>
      {state.telegraph_visible ? (
        targeted.size > 0 && (
          <div className="telegraph">
            🛰 情報研判：敵軍下一波預定攻擊 {[...targeted].join("、")}
          </div>
        )
      ) : (
        <div className="telegraph dim">
          🛰 情報不足（需 {state.telegraph_threshold}），無法研判敵軍動向 — 可執行「偵察」。
        </div>
      )}
      <motion.ul layout className="zone-list">
        {state.zones.map((z) => (
          <Zone
            key={z.code}
            zone={z}
            clickable={pending != null}
            flashed={flash[z.code] != null}
            targeted={targeted.has(z.code)}
            onPick={onPick}
          />
        ))}
      </motion.ul>
    </section>
  );
}
