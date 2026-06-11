import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { formatEffects } from "../constants.js";

// Teletype the incoming dispatch character by character.
function Typewriter({ text }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    setShown(0);
    const t = setInterval(
      () => setShown((n) => (n >= text.length ? (clearInterval(t), n) : n + 1)),
      18
    );
    return () => clearInterval(t);
  }, [text]);
  return (
    <span>
      {text.slice(0, shown)}
      {shown < text.length && <span className="caret">▌</span>}
    </span>
  );
}

function EventInner({ event, onChoose, busy }) {
  return (
    <>
      <div>
        <span className="evt-code">〔{event.code}〕</span>
        <span className="evt-title">{event.title}</span>
      </div>
      <div className="evt-desc">
        <Typewriter text={event.description} />
      </div>
      <div className="opts">
        {event.options.map((o) => (
          <motion.button
            key={o.code}
            className="opt"
            disabled={!o.affordable || busy}
            onClick={() => onChoose(o.code)}
            whileHover={o.affordable && !busy ? { scale: 1.03, y: -2 } : undefined}
            whileTap={o.affordable && !busy ? { scale: 0.97 } : undefined}
          >
            <span className="ocode">{o.code}</span>
            {o.text}
            {o.cost ? (
              <span className="cost">CP {o.cost}</span>
            ) : (
              <span className="free">免費</span>
            )}
            <div className="effects">
              {formatEffects(o.effects).map((c, i) => (
                <span key={i} className={`chip ${c.good ? "good" : "bad"}`}>
                  {c.text}
                </span>
              ))}
            </div>
          </motion.button>
        ))}
      </div>
    </>
  );
}

function CommandInner({ state, pending, onSelect, onEnd, busy }) {
  return (
    <>
      <div className="evt-title">
        指揮階段 <span className="cmd-cp">可用 CP {state.cp}</span>
      </div>
      <div className="cmds">
        {state.available_commands.map((c) => (
          <motion.button
            key={c.key}
            className={`cmd ${pending?.action === c.key ? "armed" : ""}`}
            disabled={busy}
            onClick={() => onSelect(c)}
            whileHover={!busy ? { scale: 1.03, y: -2 } : undefined}
            whileTap={!busy ? { scale: 0.97 } : undefined}
          >
            {c.label}
            {c.needs_target && <span className="need">（需選防區）</span>}
            <span className="cost">CP {c.cost}</span>
          </motion.button>
        ))}
        <motion.button
          className="done-btn"
          disabled={busy}
          onClick={onEnd}
          whileHover={!busy ? { scale: 1.05 } : undefined}
          whileTap={!busy ? { scale: 0.95 } : undefined}
        >
          結束指揮 ▶
        </motion.button>
      </div>
      <AnimatePresence>
        {pending && (
          <motion.div
            className="hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {pending.action === "deploy"
              ? `請在上方防區地圖，點選要部署「${pending.force}」的防區。`
              : "請在上方防區地圖點選目標防區。"}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default function ActionBar({
  state,
  pending,
  onChoose,
  onSelect,
  onEnd,
  busy,
}) {
  const isEvent = state.phase === "event" && state.event;
  const isCommand = state.phase === "command";
  // A single keyed child is the reliable `mode="wait"` pattern — sibling
  // conditionals can leave AnimatePresence stuck on the outgoing card.
  const key = isEvent ? `evt-${state.event.code}` : isCommand ? "cmd" : "none";

  return (
    <div id="action">
      <AnimatePresence mode="wait">
        {(isEvent || isCommand) && (
          <motion.div
            key={key}
            className="card"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ type: "spring", stiffness: 200, damping: 22 }}
          >
            {isEvent ? (
              <EventInner event={state.event} onChoose={onChoose} busy={busy} />
            ) : (
              <CommandInner
                state={state}
                pending={pending}
                onSelect={onSelect}
                onEnd={onEnd}
                busy={busy}
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
