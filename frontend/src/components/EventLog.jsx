import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef } from "react";

export default function EventLog({ entries }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [entries]);

  // Only the freshest batch is highlighted.
  const freshFrom = entries.length ? entries[entries.length - 1].batch : -1;

  return (
    <section className="panel">
      <h2>戰況紀錄</h2>
      <div id="log" ref={ref}>
        <AnimatePresence initial={false}>
          {entries.map((e) => (
            <motion.div
              key={e.key}
              className={`entry ${e.batch === freshFrom ? "fresh" : ""}`}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ type: "spring", stiffness: 220, damping: 24 }}
            >
              {e.text}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </section>
  );
}
