"use client";

import { useEffect, useState } from "react";
import {
  Users,
  TrendingUp,
  MessageCircle,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";

interface DashboardMetrics {
  total_leads: number;
  leads_novos: number;
  leads_fechados: number;
  valor_pipeline: number;
  mensagens_enviadas: number;
  taxa_resposta: number;
  taxa_conversao: number;
  leads_por_status: Record<string, number>;
  pipeline_por_etapa: Record<string, { total: number; valor: number }>;
  leads_por_dia: Array<{ dia: string; total: number }>;
  top_leads: Array<{ id: string; nome: string; score: number; status: string }>;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/relatorios/dashboard");
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error("Erro ao carregar métricas:", error);
      // Dados mock pra desenvolvimento
      setMetrics({
        total_leads: 156,
        leads_novos: 23,
        leads_fechados: 8,
        valor_pipeline: 245000,
        mensagens_enviadas: 89,
        taxa_resposta: 34.5,
        taxa_conversao: 12.8,
        leads_por_status: {
          novo: 45,
          contatado: 32,
          qualificado: 28,
          em_proposta: 18,
          fechado: 8,
          perdido: 25,
        },
        pipeline_por_etapa: {
          lead: { total: 45, valor: 120000 },
          qualificado: { total: 28, valor: 85000 },
          contato: { total: 15, valor: 45000 },
          call: { total: 8, valor: 30000 },
          proposta: { total: 5, valor: 25000 },
          fechado: { total: 8, valor: 40000 },
        },
        leads_por_dia: [
          { dia: "25/07", total: 5 },
          { dia: "26/07", total: 8 },
          { dia: "27/07", total: 3 },
          { dia: "28/07", total: 12 },
          { dia: "29/07", total: 7 },
          { dia: "30/07", total: 10 },
          { dia: "31/07", total: 6 },
        ],
        top_leads: [
          { id: "1", nome: "Roberto Lima", score: 91, status: "em_proposta" },
          { id: "2", nome: "Carlos Silva", score: 85, status: "qualificado" },
          { id: "3", nome: "Pedro Almeida", score: 78, status: "qualificado" },
          { id: "4", nome: "Ana Santos", score: 72, status: "contatado" },
          { id: "5", nome: "Mariana Costa", score: 63, status: "novo" },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!metrics) {
    return <div className="p-8">Erro ao carregar dashboard</div>;
  }

  const statCards = [
    {
      title: "Total de Leads",
      value: metrics.total_leads,
      icon: Users,
      change: "+12%",
      changeType: "positive",
      color: "bg-blue-500",
    },
    {
      title: "Leads Novos",
      value: metrics.leads_novos,
      icon: TrendingUp,
      change: "+8%",
      changeType: "positive",
      color: "bg-green-500",
    },
    {
      title: "Mensagens Enviadas",
      value: metrics.mensagens_enviadas,
      icon: MessageCircle,
      change: "+23%",
      changeType: "positive",
      color: "bg-purple-500",
    },
    {
      title: "Valor no Pipeline",
      value: `R$ ${(metrics.valor_pipeline / 1000).toFixed(0)}k`,
      icon: DollarSign,
      change: "+15%",
      changeType: "positive",
      color: "bg-orange-500",
    },
  ];

  const statusColors: Record<string, string> = {
    novo: "bg-blue-100 text-blue-800",
    contatado: "bg-yellow-100 text-yellow-800",
    qualificado: "bg-orange-100 text-orange-800",
    em_proposta: "bg-purple-100 text-purple-800",
    fechado: "bg-green-100 text-green-800",
    perdido: "bg-red-100 text-red-800",
  };

  const etapas = ["lead", "qualificado", "contato", "call", "proposta", "fechado"];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Visão geral do seu funil de vendas</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50">
            Últimos 7 dias
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            Exportar
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.title}</p>
                <p className="text-2xl font-bold mt-1">{card.value}</p>
              </div>
              <div className={`${card.color} p-3 rounded-lg`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1 text-sm">
              {card.changeType === "positive" ? (
                <ArrowUpRight className="w-4 h-4 text-green-500" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-red-500" />
              )}
              <span
                className={
                  card.changeType === "positive" ? "text-green-600" : "text-red-600"
                }
              >
                {card.change}
              </span>
              <span className="text-gray-400">vs mês anterior</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Overview */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Pipeline de Vendas</h2>
          <div className="grid grid-cols-6 gap-2">
            {etapas.map((etapa) => {
              const data = metrics.pipeline_por_etapa[etapa];
              return (
                <div key={etapa} className="text-center">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-2xl font-bold">{data?.total || 0}</p>
                    <p className="text-xs text-gray-500 capitalize">{etapa}</p>
                  </div>
                  <p className="text-xs mt-1 text-gray-400">
                    R$ {((data?.valor || 0) / 1000).toFixed(0)}k
                  </p>
                </div>
              );
            })}
          </div>

          {/* Bar visual */}
          <div className="mt-6 flex gap-1 h-8 rounded-lg overflow-hidden">
            {etapas.map((etapa) => {
              const total = metrics.pipeline_por_etapa[etapa]?.total || 0;
              const maxTotal = Math.max(...etapas.map((e) => metrics.pipeline_por_etapa[e]?.total || 0));
              const width = maxTotal > 0 ? (total / maxTotal) * 100 : 0;
              const colors = ["bg-blue-400", "bg-cyan-400", "bg-yellow-400", "bg-orange-400", "bg-purple-400", "bg-green-400"];
              const index = etapas.indexOf(etapa);
              return (
                <div
                  key={etapa}
                  className={`${colors[index]} transition-all duration-500`}
                  style={{ width: `${Math.max(width, 5)}%` }}
                  title={`${etapa}: ${total}`}
                />
              );
            })}
          </div>
        </div>

        {/* Top Leads */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Top Leads</h2>
          <div className="space-y-3">
            {metrics.top_leads.map((lead, index) => (
              <div
                key={lead.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-gray-400">#{index + 1}</span>
                  <div>
                    <p className="font-medium text-sm">{lead.nome}</p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${statusColors[lead.status] || "bg-gray-100"}`}
                    >
                      {lead.status}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-blue-600">{lead.score}</span>
                  <p className="text-xs text-gray-400">score</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leads por Status */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Leads por Status</h2>
          <div className="space-y-3">
            {Object.entries(metrics.leads_por_status).map(([status, count]) => {
              const total = Object.values(metrics.leads_por_status).reduce((a, b) => a + b, 0);
              const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : "0";
              return (
                <div key={status} className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full capitalize ${statusColors[status] || "bg-gray-100"}`}>
                    {status}
                  </span>
                  <div className="flex-1 bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-12 text-right">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Métricas de Performance */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Performance</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-green-600">{metrics.taxa_resposta}%</p>
              <p className="text-sm text-gray-500 mt-1">Taxa de Resposta</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-blue-600">{metrics.taxa_conversao}%</p>
              <p className="text-sm text-gray-500 mt-1">Taxa de Conversão</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-purple-600">{metrics.leads_fechados}</p>
              <p className="text-sm text-gray-500 mt-1">Fechados</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-orange-600">
                R$ {metrics.leads_fechados > 0 ? ((metrics.valor_pipeline * 0.15) / metrics.leads_fechados / 1000).toFixed(1) : 0}k
              </p>
              <p className="text-sm text-gray-500 mt-1">Ticket Médio</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
