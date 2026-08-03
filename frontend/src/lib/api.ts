/**
 * LeadFlow - API Client
 */

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor pra adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("leadflow_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor pra tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("leadflow_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ============== LEADS ==============

export const leadsApi = {
  list: (params?: Record<string, any>) => api.get("/leads", { params }),
  get: (id: string) => api.get(`/leads/${id}`),
  create: (data: any) => api.post("/leads", data),
  update: (id: string, data: any) => api.put(`/leads/${id}`, data),
  delete: (id: string) => api.delete(`/leads/${id}`),
  historico: (id: string) => api.get(`/leads/${id}/historico`),
};

// ============== PIPELINE ==============

export const pipelineApi = {
  get: () => api.get("/pipeline"),
  metrics: () => api.get("/pipeline/metrics"),
  create: (data: any) => api.post("/pipeline", data),
  move: (id: string, etapa: string, motivo?: string) =>
    api.put(`/pipeline/${id}/mover`, { etapa, motivo_perda: motivo }),
  delete: (id: string) => api.delete(`/pipeline/${id}`),
};

// ============== WHATSAPP ==============

export const whatsappApi = {
  status: () => api.get("/whatsapp/status"),
  enviar: (data: any) => api.post("/whatsapp/enviar", data),
  mensagens: (leadId: string, params?: any) =>
    api.get(`/whatsapp/mensagens/${leadId}`, { params }),
  followUp: (leadId: string) => api.post(`/whatsapp/follow-up/${leadId}`),
};

// ============== IA ==============

export const iaApi = {
  gerarMensagem: (data: any) => api.post("/ia/gerar-mensagem", data),
  calcularScore: (leadId: string) => api.post(`/ia/score/${leadId}`),
  qualificar: (leadId: string) => api.post(`/ia/qualificar/${leadId}`),
  melhorHorario: (leadId: string) => api.post(`/ia/melhor-horario/${leadId}`),
  abTest: (leadId: string, variacoes?: number) =>
    api.post("/ia/ab-test", { lead_id: leadId, variacoes }),
};

// ============== COLETA ==============

export const coletaApi = {
  googleMaps: (data: any) => api.post("/coleta/google-maps", data),
  instagram: (data: any) => api.post("/coleta/instagram", data),
  linkedin: (data: any) => api.post("/coleta/linkedin", data),
  cnpj: (data: any) => api.post("/coleta/cnpj", data),
  importarCnpj: (cnpj: string) => api.post(`/coleta/cnpj/${cnpj}/importar`),
};

// ============== RELATÓRIOS ==============

export const relatoriosApi = {
  dashboard: (periodo?: number) =>
    api.get("/relatorios/dashboard", { params: { periodo } }),
  conversao: (periodo?: number) =>
    api.get("/relatorios/conversao", { params: { periodo } }),
  roi: (periodo?: number) =>
    api.get("/relatorios/roi", { params: { periodo } }),
  exportarLeads: (status?: string) =>
    api.get("/relatorios/exportar/leads", { params: { status }, responseType: "blob" }),
  exportarPipeline: () =>
    api.get("/relatorios/exportar/pipeline", { responseType: "blob" }),
};

export default api;
