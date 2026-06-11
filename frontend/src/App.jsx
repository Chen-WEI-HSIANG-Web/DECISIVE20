import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import * as api from "./api.js";
import Header from "./components/Header.jsx";
import ResourcePanel from "./components/ResourcePanel.jsx";
import ForcePanel from "./components/ForcePanel.jsx";
import ZoneMap from "./components/ZoneMap.jsx";
import EventLog from "./components/EventLog.jsx";
import ActionBar from "./components/ActionBar.jsx";
import EndOverlay from "./components/EndOverlay.jsx";
import SetupScreen from "./components/SetupScreen.jsx";
import RoundBanner, { roundClock } from "./components/RoundBanner.jsx";

export default function App() {
  const [screen, setScreen] = useState("setup"); // "setup" | "game"
  const [state, setState] = useState(null);
  const [gameId, setGameId] = useState(null);
  const [log, setLog] = useState([]);
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState(null); // { round, total }
  const [alert, setAlert] = useState(false); // red vignette during enemy strikes

  const logSeq = useRef(0);
  const batchSeq = useRef(0);
  const prevZones = useRef({});
  const prevRound = useRef(0);
  const [flash, setFlash] = useState({});

  const pushLog = useCallback((messages, reset, round) => {
    const batch = batchSeq.current++;
    const items = (messages || []).map((text) => ({
      key: logSeq.current++,
      text,
      batch,
      time: roundClock(round),
    }));
    setLog((prev) => (reset ? items : [...prev, ...items]));
  }, []);

  const apply = useCallback(
    (snap, isNew) => {
      setState(snap);
      if (snap.game_id) setGameId(snap.game_id);
      pushLog(snap.messages, isNew, snap.round);
      setPending(null);

      // Round banner whenever a new round opens (including the first).
      if (snap.round !== prevRound.current && snap.phase !== "ended") {
        prevRound.current = snap.round;
        setBanner({ round: snap.round, total: snap.total_rounds });
      }
      // Red-alert vignette while the enemy assault report comes in.
      const hostile = (snap.messages || []).some(
        (m) => m.includes("敵軍發動") || m.includes("遭突破") || m.includes("失守")
      );
      if (hostile) setAlert(true);
    },
    [pushLog]
  );

  // Auto-dismiss the round banner / red alert.
  useEffect(() => {
    if (!banner) return;
    const t = setTimeout(() => setBanner(null), 1700);
    return () => clearTimeout(t);
  }, [banner]);
  useEffect(() => {
    if (!alert) return;
    const t = setTimeout(() => setAlert(false), 1400);
    return () => clearTimeout(t);
  }, [alert]);

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

  const startGame = useCallback(
    async (config) => {
      prevZones.current = {};
      prevRound.current = 0;
      await step(() => api.newGame(config), true);
      setScreen("game");
    },
    [step]
  );

  const backToSetup = useCallback(() => {
    setScreen("setup");
    setState(null);
    setGameId(null);
    setLog([]);
    setPending(null);
    setBanner(null);
  }, []);

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
      setPending({ action: cmd.key });
    } else {
      step(() => api.runCommand(gameId, cmd.key, null));
    }
  };
  const onDeploy = (forceName) => {
    if (state.phase !== "command") return;
    setPending({ action: "deploy", force: forceName });
  };
  const onPickZone = (code) => {
    if (!pending) return;
    const { action, force } = pending;
    setPending(null);
    step(() => api.runCommand(gameId, action, code, force));
  };
  const onEnd = () => step(() => api.endCommand(gameId));

  if (screen === "setup" || !state) {
    return (
      <>
        <SetupScreen onStart={startGame} busy={busy} />
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

  return (
    <div className={alert ? "shake" : ""}>
      <Header state={state} onNewGame={backToSetup} busy={busy} />
      <main>
        <div className="col">
          <ResourcePanel state={state} />
          <ForcePanel
            state={state}
            pending={pending}
            onDeploy={onDeploy}
            busy={busy}
          />
        </div>
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
      <RoundBanner banner={banner} />
      <AnimatePresence>
        {alert && <motion.div
          className="alert-vignette"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />}
      </AnimatePresence>
      <EndOverlay state={state} onNewGame={backToSetup} />
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
    </div>
  );
}
