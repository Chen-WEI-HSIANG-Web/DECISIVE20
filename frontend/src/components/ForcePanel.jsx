import { motion } from "framer-motion";

export default function ForcePanel({ state, pending, onDeploy, busy }) {
  const canDeploy = state.can_deploy;
  return (
    <section className="panel">
      <h2>部隊</h2>
      <ul className="force-list">
        {state.forces.map((f) => {
          const armed = pending?.action === "deploy" && pending.force === f.name;
          const depleted = f.value <= 0;
          const ready = canDeploy && !depleted && !busy;
          return (
            <li key={f.name} className={`force ${armed ? "armed" : ""}`}>
              <div className="fmain">
                <span className="fname">{f.name}</span>
                <span className="fval">戰力 {f.value}</span>
              </div>
              <div className="floc">
                {depleted
                  ? "已潰散"
                  : f.assigned_zone
                  ? `駐防 ${f.assigned_zone}`
                  : "待命中"}
              </div>
              <motion.button
                className="deploy-btn"
                disabled={!ready}
                onClick={() => onDeploy(f.name)}
                whileHover={ready ? { scale: 1.04 } : undefined}
                whileTap={ready ? { scale: 0.96 } : undefined}
              >
                {armed ? "選擇防區…" : `部署（CP ${state.deploy_cost}）`}
              </motion.button>
            </li>
          );
        })}
      </ul>
      <p className="force-hint">部署後，該區遭突破時由駐軍承受衝擊，守住陣地。</p>
    </section>
  );
}
