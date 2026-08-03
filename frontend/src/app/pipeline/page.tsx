"use client";

import { useEffect, useState } from "react";
import { GripVertical, Plus, MoreVertical, DollarSign, Calendar } from "lucide-react";

interface PipelineItem {
  id: string;
  lead_id: string;
  lead_nome: string;
  lead_score: number;
  lead_empresa: string;
  valor: number;
  probabilidade: number;
  data_previsao: string;
  moved_at: string;
}

interface PipelineData {
  lead: PipelineItem[];
  qualificado: PipelineItem[];
  contato: PipelineItem[];
  call: PipelineItem[];
  proposta: PipelineItem[];
  fechado: PipelineItem[];
}

const colunas = [
  { key: "lead", label: "Lead", color: "bg-blue-500" },
  { key: "qualificado", label: "Qualificado", color: "bg-cyan-500" },
  { key: "contato", label: "Contato", color: "bg-yellow-500" },
  { key: "call", label: "Call", color: "bg-orange-500" },
  { key: "proposta", label: "Proposta", color: "bg-purple-500" },
  { key: "fechado", label: "Fechado", color: "bg-green-500" },
];

export default function PipelinePage() {
  const [pipeline, setPipeline] = useState<PipelineData>({
    lead: [],
    qualificado: [],
    contato: [],
    call: [],
    proposta: [],
    fechado: [],
  });
  const [loading, setLoading] = useState(true);
  const [draggedItem, setDraggedItem] = useState<PipelineItem | null>(null);

  useEffect(() => {
    fetchPipeline();
  }, []);

  const fetchPipeline = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/pipeline");
      if (response.ok) {
        const data = await response.json();
        setPipeline(data);
      }
    } catch (error) {
      // Mock data
      setPipeline({
        lead: [
          { id: "1", lead_id: "4", lead_nome: "Mariana Costa", lead_score: 63, lead_empresa: "EcomEx", valor: 8000, probabilidade: 15, data_previsao: "2024-03-15", moved_at: "2024-01-15" },
          { id: "6", lead_id: "6", lead_nome: "Lucas Ferreira", lead_score: 45, lead_empresa: "StartupXYZ", valor: 5000, probabilidade: 10, data_previsao: "2024-04-01", moved_at: "2024-01-14" },
        ],
        qualificado: [
          { id: "2", lead_id: "1", lead_nome: "Carlos Silva", lead_score: 85, lead_empresa: "TechSol", valor: 15000, probabilidade: 60, data_previsao: "2024-02-15", moved_at: "2024-01-15" },
          { id: "3", lead_id: "5", lead_nome: "Pedro Almeida", lead_score: 78, lead_empresa: "SaúdeDig", valor: 30000, probabilidade: 50, data_previsao: "2024-02-28", moved_at: "2024-01-14" },
        ],
        contato: [
          { id: "4", lead_id: "2", lead_nome: "Ana Santos", lead_score: 72, lead_empresa: "MD Pro", valor: 5000, probabilidade: 30, data_previsao: "2024-03-01", moved_at: "2024-01-13" },
        ],
        call: [],
        proposta: [
          { id: "5", lead_id: "3", lead_nome: "Roberto Lima", lead_score: 91, lead_empresa: "FinABC", valor: 50000, probabilidade: 75, data_previsao: "2024-02-01", moved_at: "2024-01-15" },
        ],
        fechado: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (item: PipelineItem) => {
    setDraggedItem(item);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (targetEtapa: string) => {
    if (!draggedItem) return;

    // Encontra etapa atual
    let sourceEtapa = "";
    for (const [etapa, items] of Object.entries(pipeline)) {
      if (items.find((i) => i.id === draggedItem.id)) {
        sourceEtapa = etapa;
        break;
      }
    }

    if (sourceEtapa === targetEtapa) {
      setDraggedItem(null);
      return;
    }

    // Move no estado local
    const newPipeline = { ...pipeline };
    newPipeline[sourceEtapa] = newPipeline[sourceEtapa].filter(
      (i) => i.id !== draggedItem.id
    );
    newPipeline[targetEtapa] = [...newPipeline[targetEtapa], draggedItem];
    setPipeline(newPipeline);
    setDraggedItem(null);

    // Chama API
    try {
      await fetch(`http://localhost:8000/api/pipeline/${draggedItem.id}/mover`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ etapa: targetEtapa }),
      });
    } catch (error) {
      console.error("Erro ao mover:", error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-100 text-green-700";
    if (score >= 50) return "bg-yellow-100 text-yellow-700";
    return "bg-red-100 text-red-700";
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  };

  const getEtapaMetrics = (etapa: string) => {
    const items = pipeline[etapa as keyof PipelineData] || [];
    const totalValor = items.reduce((acc, item) => acc + item.valor, 0);
    return { total: items.length, valor: totalValor };
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Pipeline de Vendas</h1>
          <p className="text-gray-500">Arraste os cards entre as etapas</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Adicionar ao Pipeline
        </button>
      </div>

      {/* Pipeline */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="grid grid-cols-6 gap-4 overflow-x-auto">
          {colunas.map((coluna) => {
            const metrics = getEtapaMetrics(coluna.key);
            const items = pipeline[coluna.key as keyof PipelineData] || [];

            return (
              <div
                key={coluna.key}
                className="min-w-[250px]"
                onDragOver={handleDragOver}
                onDrop={() => handleDrop(coluna.key)}
              >
                {/* Column Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${coluna.color}`} />
                    <h3 className="font-medium text-sm">{coluna.label}</h3>
                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                      {metrics.total}
                    </span>
                  </div>
                </div>

                {/* Column Metrics */}
                <div className="bg-gray-50 rounded-lg p-2 mb-3 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Valor:</span>
                    <span className="font-medium">{formatCurrency(metrics.valor)}</span>
                  </div>
                </div>

                {/* Cards */}
                <div className="space-y-2 kanban-column">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      draggable
                      onDragStart={() => handleDragStart(item)}
                      className="kanban-card bg-white rounded-lg border p-3 cursor-grab active:cursor-grabbing"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{item.lead_nome}</p>
                          <p className="text-xs text-gray-500">{item.lead_empresa}</p>
                        </div>
                        <button className="p-1 hover:bg-gray-100 rounded">
                          <MoreVertical className="w-3 h-3 text-gray-400" />
                        </button>
                      </div>

                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getScoreColor(item.lead_score)}`}>
                          Score: {item.lead_score}
                        </span>
                        <span className="text-xs text-gray-400">
                          {item.probabilidade}%
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <DollarSign className="w-3 h-3" />
                          {formatCurrency(item.valor)}
                        </div>
                        {item.data_previsao && (
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(item.data_previsao).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {items.length === 0 && (
                    <div className="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center text-sm text-gray-400">
                      Arraste leads aqui
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
