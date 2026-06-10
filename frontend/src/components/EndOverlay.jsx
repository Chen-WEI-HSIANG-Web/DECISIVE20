import { motion, AnimatePresence } from "framer-motion";
import { ENDING_LABEL, ENDING_VAR } from "../constants.js";

export default function EndOverlay({ state, onNewGame }) {
  const show = state?.phase === "ended";
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="result"
            initial={{ scale: 0.7, y: 30, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness: 180, damping: 16 }}
          >
            <div
              className="verdict"
              style={{ color: ENDING_VAR[state.ending_type] }}
            >
              {ENDING_LABEL[state.ending_type] || "結束"}
            </div>
            <motion.div
              className="rank"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.25, type: "spring", stiffness: 260, damping: 12 }}
            >
              {state.rank}
            </motion.div>
            <div className="score">
              最終評分 {state.score}　存活 {state.round}/{state.total_rounds} 回合
            </div>
            <motion.button
              onClick={onNewGame}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              再玩一局
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
