import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const client = axios.create({ baseURL: API });

export const api = {
  listPlayers: (params = {}) => client.get("/players", { params }).then((r) => r.data),
  getPlayer: (id) => client.get(`/players/${id}`).then((r) => r.data),
  mlbReference: () => client.get("/mlb-reference").then((r) => r.data),
  mlbPlayer: (id) => client.get(`/mlb-reference/${id}`).then((r) => r.data),
  getShortlist: () => client.get("/shortlist").then((r) => r.data),
  addShortlist: (id) => client.post(`/shortlist/${id}`).then((r) => r.data),
  removeShortlist: (id) => client.delete(`/shortlist/${id}`).then((r) => r.data),
  analyzeBiomech: (playerId, file) => {
    const fd = new FormData();
    if (file) fd.append("file", file);
    const qp = playerId ? `?player_id=${playerId}` : "";
    return client.post(`/biomech/analyze${qp}`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  reportUrl: (id) => `${API}/players/${id}/report`,
  statsSummary: () => client.get("/stats/summary").then((r) => r.data),
};

export default api;
