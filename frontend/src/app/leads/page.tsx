"use client";

import { useEffect, useState } from "react";
import { Search, Filter, Plus, Download, MoreVertical, Mail, Phone, MessageCircle } from "lucide-react";

interface Lead {
  id: string;
  nome: string;
  cargo: string;
  email: string;
  telefone: string;
  whatsapp: string;
  score: number;
  status: string;
  fonte: string;
  empresa: string;
  ultimo_contato: string;
}

const statusColors: Record<string, string> = {
  novo: "bg-blue-100 text-blue-800",
  contatado: "bg-yellow-100 text-yellow-800",
  qualificado: "bg-orange-100 text-orange-800",
  em_proposta: "bg-purple-100 text-purple-800",
  fechado: "bg-green-100 text-green-800",
  perdido: "bg-red-100 text-red-800",
};

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (statusFilter) params.append("status", statusFilter);

      const response = await fetch(`http://localhost:8000/api/leads?${params}`);
      if (response.ok) {
        const data = await response.json();
        setLeads(data);
      }
    } catch (error) {
      // Mock data
      setLeads([
        { id: "1", nome: "Carlos Silva", cargo: "CTO", email: "carlos@techsol.com", telefone: "11999887700", whatsapp: "5511999887700", score: 85, status: "qualificado", fonte: "google_maps", empresa: "TechSol", ultimo_contato: "2024-01-15" },
        { id: "2", nome: "Ana Santos", cargo: "CEO", email: "ana@mdpro.com", telefone: "21988776600", whatsapp: "5521988776600", score: 72, status: "contatado", fonte: "instagram", empresa: "MD Pro", ultimo_contato: "2024-01-14" },
        { id: "3", nome: "Roberto Lima", cargo: "Diretor Comercial", email: "roberto@finabc.com", telefone: "31977665500", whatsapp: "5531977665500", score: 91, status: "em_proposta", fonte: "linkedin", empresa: "FinABC", ultimo_contato: "2024-01-15" },
        { id: "4", nome: "Mariana Costa", cargo: "Head de Growth", email: "mariana@ecomex.com", telefone: "41966554400", whatsapp: "5541966554400", score: 63, status: "novo", fonte: "google_maps", empresa: "EcomEx", ultimo_contato: null },
        { id: "5", nome: "Pedro Almeida", cargo: "VP de Tecnologia", email: "pedro@saudedig.com", telefone: "61955443300", whatsapp: "5561955443300", score: 78, status: "qualificado", fonte: "receita_federal", empresa: "SaúdeDig", ultimo_contato: "2024-01-13" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 bg-green-50";
    if (score >= 50) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Leads</h1>
          <p className="text-gray-500">{leads.length} leads cadastrados</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50 flex items-center gap-2">
            <Download className="w-4 h-4" />
            Exportar
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Novo Lead
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Buscar leads..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos os status</option>
          <option value="novo">Novo</option>
          <option value="contatado">Contatado</option>
          <option value="qualificado">Qualificado</option>
          <option value="em_proposta">Em Proposta</option>
          <option value="fechado">Fechado</option>
          <option value="perdido">Perdido</option>
        </select>
        <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Filtros
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lead</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Empresa</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fonte</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contato</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  Carregando...
                </td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  Nenhum lead encontrado
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium">{lead.nome}</p>
                      <p className="text-sm text-gray-500">{lead.cargo}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">{lead.empresa || "-"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${getScoreColor(lead.score)}`}>
                      {lead.score}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs ${statusColors[lead.status] || "bg-gray-100"}`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{lead.fonte}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      {lead.email && (
                        <button className="p-1 hover:bg-gray-100 rounded" title="Email">
                          <Mail className="w-4 h-4 text-gray-400" />
                        </button>
                      )}
                      {lead.telefone && (
                        <button className="p-1 hover:bg-gray-100 rounded" title="Telefone">
                          <Phone className="w-4 h-4 text-gray-400" />
                        </button>
                      )}
                      {lead.whatsapp && (
                        <button className="p-1 hover:bg-gray-100 rounded" title="WhatsApp">
                          <MessageCircle className="w-4 h-4 text-green-500" />
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <MoreVertical className="w-4 h-4 text-gray-400" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
