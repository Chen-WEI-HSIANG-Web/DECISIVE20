async function request(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

export const listScenarios = () => request("GET", "/api/scenarios");
// config: { scenario, seed, victory_conditions, failure_conditions } — all optional.
export const newGame = (config) => request("POST", "/api/games", config || {});
export const chooseEvent = (id, option) =>
  request("POST", `/api/games/${id}/event`, { option });
export const runCommand = (id, action, target, force) =>
  request("POST", `/api/games/${id}/command`, { action, target, force });
export const endCommand = (id) =>
  request("POST", `/api/games/${id}/end-command`);
