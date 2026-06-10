import { motion } from "framer-motion";
import { RES_DEF } from "../constants.js";
import { useCountUp } from "../useCountUp.js";

function ResourceRow({ label, value, max, danger, warn }) {
  const display = useCountUp(value);
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const color = danger ? "var(--red)" : warn ? "var(--yellow)" : "var(--green)";
  const cls = danger ? "danger" : warn ? "warn" : "";
  return (
    <div className="res">
      <div className="label">
        <span>{label}</span>
        <span className={`val ${cls}`}>
          {display}
          {danger && <span className="warn-tag">⚠ 危險</span>}
          {!danger && warn && <span className="warn-tag">⚠</span>}
        </span>
      </div>
      <div className="bar">
        <motion.span
          animate={{
            width: `${pct}%`,
            backgroundColor: color,
            opacity: danger ? [1, 0.55, 1] : 1,
          }}
          transition={{
            width: { type: "spring", stiffness: 120, damping: 18 },
            backgroundColor: { duration: 0.3 },
            opacity: danger
              ? { duration: 1.1, repeat: Infinity }
              : { duration: 0.2 },
          }}
        />
      </div>
    </div>
  );
}

export default function ResourcePanel({ state }) {
  return (
    <section className="panel">
      <h2>資源面板</h2>
      <div>
        {RES_DEF.map(([label, key, max, isDanger, isWarn]) => {
          const v = state.resources[key];
          const danger = isDanger(v);
          return (
            <ResourceRow
              key={key}
              label={label}
              value={v}
              max={max}
              danger={danger}
              warn={!danger && isWarn(v)}
            />
          );
        })}
      </div>
    </section>
  );
}
