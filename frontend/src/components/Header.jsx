import { motion } from "framer-motion";
import { useCountUp } from "../useCountUp.js";

export default function Header({ state, onNewGame, busy }) {
  const cp = useCountUp(state?.cp ?? 0);
  return (
    <header>
      <h1>決戰20</h1>
      <span className="scenario">{state?.scenario_name ?? "—"}</span>
      {state && (
        <span className="round">
          第 {state.round} / {state.total_rounds} 回合
        </span>
      )}
      <span className="cp">
        指令點 CP{" "}
        <motion.b
          key={state?.cp}
          initial={{ scale: 1.5, color: "#7ee787" }}
          animate={{ scale: 1, color: "#3fb950" }}
          transition={{ duration: 0.35 }}
        >
          {cp}
        </motion.b>
      </span>
      <motion.button
        onClick={onNewGame}
        disabled={busy}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        新對局
      </motion.button>
    </header>
  );
}
