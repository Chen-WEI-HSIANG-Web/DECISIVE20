import { motion, AnimatePresence } from "framer-motion";

// Fictional military clock: each round is one phase of the day starting 0500.
export function roundClock(round) {
  const hour = (5 + (round - 1) * 3) % 24;
  const day = 1 + Math.floor(((round - 1) * 3 + 5) / 24);
  return `D+${day} ${String(hour).padStart(2, "0")}00時`;
}

export default function RoundBanner({ banner }) {
  return (
    <AnimatePresence>
      {banner && (
        <motion.div
          key={banner.round}
          className="round-banner"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <motion.div
            className="rb-inner"
            initial={{ scale: 0.8, letterSpacing: "18px" }}
            animate={{ scale: 1, letterSpacing: "8px" }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
          >
            <div className="rb-clock">{roundClock(banner.round)}</div>
            <div className="rb-round">第 {banner.round} 回合</div>
            <div className="rb-total">／ 共 {banner.total} 回合</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
