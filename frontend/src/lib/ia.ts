/**
 * LeadFlow - IA Helper Functions
 */

export interface ScoreResult {
  score: number;
  classificacao: "quente" | "morno" | "frio";
  detalhes: Record<string, number>;
  recomendacao: string;
}

export interface MensagemGerada {
  mensagem: string;
  modelo: string;
  tokens: number;
}

/**
 * Cor do score
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 50) return "text-yellow-600";
  return "text-red-600";
}

/**
 * Background do score
 */
export function getScoreBgColor(score: number): string {
  if (score >= 80) return "bg-green-100";
  if (score >= 50) return "bg-yellow-100";
  return "bg-red-100";
}

/**
 * Badge do score
 */
export function getScoreBadge(score: number): {
  label: string;
  color: string;
  bgColor: string;
} {
  if (score >= 80) {
    return { label: "Quente", color: "text-green-700", bgColor: "bg-green-100" };
  }
  if (score >= 50) {
    return { label: "Morno", color: "text-yellow-700", bgColor: "bg-yellow-100" };
  }
  return { label: "Frio", color: "text-red-700", bgColor: "bg-red-100" };
}

/**
 * Calcula score baseado em dados do lead (client-side)
 */
export function calcularScoreLocal(lead: {
  cargo?: string;
  funcionarios?: number;
  engajamento?: number;
  campos_preenchidos?: number;
  total_campos?: number;
}): number {
  let score = 0;

  // Tamanho empresa (0-25)
  if (lead.funcionarios) {
    if (lead.funcionarios >= 100) score += 25;
    else if (lead.funcionarios >= 50) score += 20;
    else if (lead.funcionarios >= 10) score += 15;
    else score += 5;
  }

  // Cargo (0-20)
  const cargo = (lead.cargo || "").toLowerCase();
  if (["ceo", "cto", "cfo", "diretor", "vp", "socio"].some((c) => cargo.includes(c))) {
    score += 20;
  } else if (["gerente", "head", "diretor"].some((c) => cargo.includes(c))) {
    score += 15;
  } else if (["coordenador", "analista"].some((c) => cargo.includes(c))) {
    score += 10;
  }

  // Engajamento (0-30)
  score += Math.min((lead.engajamento || 0) * 0.3, 30);

  // Perfil completo (0-25)
  if (lead.campos_preenchidos && lead.total_campos) {
    score += (lead.campos_preenchidos / lead.total_campos) * 25;
  }

  return Math.min(Math.round(score), 100);
}

/**
 * Gera mensagem de follow-up baseada no estágio
 */
export function getSuggestedFollowUp(
  diasSemContato: number,
  status: string
): string {
  if (diasSemContato <= 3) {
    return "Oi! Enviei uma mensagem há alguns dias. Teve chance de ver? Posso enviar mais detalhes?";
  }

  if (diasSemContato <= 7) {
    return "Olá! Ainda acredito que faz sentido conversarmos. Posso te enviar um case study?";
  }

  if (diasSemContato <= 14) {
    return "Oi! Estou finalizando uma rodada de prospecção. Se tiver interesse, posso reservar um horário pra gente conversar.";
  }

  return "Olá! Faz um tempo que não conversamos. Alguma coisa mudou na sua agenda? Estou à disposição!";
}

/**
 * Melhor horário baseado no cargo
 */
export function getMelhorHorario(cargo?: string): {
  dia: string;
  horario: string;
} {
  const cargoLower = (cargo || "").toLowerCase();

  if (["ceo", "diretor", "vp"].some((c) => cargoLower.includes(c))) {
    return { dia: "Terça ou Quarta", horario: "9h-11h" };
  }

  if (["gerente", "head"].some((c) => cargoLower.includes(c))) {
    return { dia: "Terça a Quinta", horario: "10h-12h" };
  }

  return { dia: "Segunda a Sexta", horario: "14h-16h" };
}
