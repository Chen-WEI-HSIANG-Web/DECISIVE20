import { motion, AnimatePresence } from "framer-motion";
import { STATUS_LABEL, STATUS_VAR } from "../constants.js";

function Zone({ zone, clickable, flashed, onPick }) {
  const dpct = Math.max(0, Math.min(100, (zone.defense / 10) * 100));
  return (
    <motion.li
      layout
      className={`zone ${clickable ? "clickable" : ""}`}
      style={{ borderLeftColor: STATUS_VAR[zone.status] }}
      animate={{ borderLeftColor: STATUS_VAR[zone.status] }}
      onClick={clickable ? () => onPick(zone.code) : undefined}
      whileHover={clickable ? { scale: 1.02, x: 3 } : undefined}
    >
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
  return (
    <section className="panel">
      <h2>防區地圖</h2>
      <motion.ul layout className="zone-list">
        {state.zones.map((z) => (
          <Zone
            key={z.code}
            zone={z}
            clickable={pending != null}
            flashed={flash[z.code] != null}
            onPick={onPick}
          />
        ))}
      </motion.ul>
    </section>
  );
}
