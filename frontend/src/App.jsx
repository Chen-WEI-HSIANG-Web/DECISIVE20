import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import * as api from "./api.js";
import Header from "./components/Header.jsx";
import ResourcePanel from "./components/ResourcePanel.jsx";
import ZoneMap from "./components/ZoneMap.jsx";
import EventLog from "./components/EventLog.jsx";
import ActionBar from "./components/ActionBar.jsx";
import EndOverlay from "./components/EndOverlay.jsx";

export default function App() {
  const [state, setState] = useState(null);
  const [gameId, setGameId] = useState(null);
  const [log, setLog] = useState([]);
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const logSeq = useRef(0);
  const batchSeq = useRef(0);
  const prevZones = useRef({});
  const [flash, setFlash] = useState({});

  const pushLog = useCallback((messages, reset) => {
    const batch = batchSeq.current++;
    const items = (messages || []).map((text) => ({
      key: logSeq.current++,
      text,
      batch,
    }));
    setLog((prev) => (reset ? items : [...prev, ...items]));
  }, []);

  const apply = useCallback(
    (snap, isNew) => {
      setState(snap);
      if (snap.game_id) setGameId(snap.game_id);
      pushLog(snap.messages, isNew);
      setPending(null);
    },
    [pushLog]
  );

  const step = useCallback(
    async (fn, isNew) => {
      setBusy(true);
      setError(null);
      try {
        const snap = await fn();
        apply(snap, isNew);
      } catch (e) {
        setError(e.message);
      } finally {
        setBusy(false);
      }
    },
    [apply]
  );

  const startGame = useCallback(() => {
    prevZones.current = {};
    step(() => api.newGame(), true);
  }, [step]);

  useEffect(() => {
    startGame();
  }, [startGame]);

  // Flash a zone whose status changed since the last snapshot.
  useEffect(() => {
    if (!state) return;
    const next = {};
    const fresh = {};
    state.zones.forEach((z) => {
      const before = prevZones.current[z.code];
      if (before && before !== z.status) fresh[z.code] = z.status;
      next[z.code] = z.status;
    });
    prevZones.current = next;
    if (Object.keys(fresh).length) {
      setFlash(fresh);
      const t = setTimeout(() => setFlash({}), 950);
      return () => clearTimeout(t);
    }
  }, [state]);

  // Auto-dismiss error toast.
  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => setError(null), 2800);
    return () => clearTimeout(t);
  }, [error]);

  const onChoose = (option) => step(() => api.chooseEvent(gameId, option));
  const onSelect = (cmd) => {
    if (cmd.needs_target) {
      setPending(cmd.key);
    } else {
      step(() => api.runCommand(gameId, cmd.key, null));
    }
  };
  const onPickZone = (code) => {
    if (!pending) return;
    const action = pending;
    setPending(null);
    step(() => api.runCommand(gameId, action, code));
  };
  const onEnd = () => step(() => api.endCommand(gameId));

  if (!state) {
    return <div className="loading">載入中…</div>;
  }

  return (
    <>
      <Header state={state} onNewGame={startGame} busy={busy} />
      <main>
        <ResourcePanel state={state} />
        <ZoneMap state={state} pending={pending} flash={flash} onPick={onPickZone} />
        <EventLog entries={log} />
      </main>
      <ActionBar
        state={state}
        pending={pending}
        onChoose={onChoose}
        onSelect={onSelect}
        onEnd={onEnd}
        busy={busy}
      />
      <EndOverlay state={state} onNewGame={startGame} />
      <AnimatePresence>
        {error && (
          <motion.div
            className="toast"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
