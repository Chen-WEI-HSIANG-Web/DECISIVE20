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

export const newGame = (seed) =>
  request("POST", "/api/games", seed != null ? { seed } : {});
export const chooseEvent = (id, option) =>
  request("POST", `/api/games/${id}/event`, { option });
export const runCommand = (id, action, target, force) =>
  request("POST", `/api/games/${id}/command`, { action, target, force });
export const endCommand = (id) =>
  request("POST", `/api/games/${id}/end-command`);
