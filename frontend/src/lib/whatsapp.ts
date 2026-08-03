/**
 * LeadFlow - WhatsApp Integration Helper
 */

export interface WhatsAppMessage {
  id: string;
  phone: string;
  message: string;
  status: "enviada" | "entregue" | "lida" | "erro";
  timestamp: Date;
  isFromLead: boolean;
}

export interface WhatsAppStatus {
  connected: boolean;
  instance: string;
  battery?: number;
  phone?: string;
}

/**
 * Formata número de telefone pra WhatsApp
 */
export function formatPhone(phone: string): string {
  // Remove tudo que não é número
  const cleaned = phone.replace(/\D/g, "");

  // Adiciona código do país se não tiver
  if (!cleaned.startsWith("55")) {
    return `55${cleaned}`;
  }

  return cleaned;
}

/**
 * Valida se número tem formato de WhatsApp brasileiro
 */
export function isValidWhatsAppNumber(phone: string): boolean {
  const cleaned = phone.replace(/\D/g, "");
  // Formato: 55 + DDD (2 dígitos) + número (8-9 dígitos)
  return /^55\d{10,11}$/.test(cleaned);
}

/**
 * Formata número pra exibição
 */
export function formatPhoneDisplay(phone: string): string {
  const cleaned = phone.replace(/\D/g, "");

  if (cleaned.length === 13 && cleaned.startsWith("55")) {
    // +55 (XX) XXXXX-XXXX
    return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 9)}-${cleaned.slice(9)}`;
  }

  if (cleaned.length === 12 && cleaned.startsWith("55")) {
    // +55 (XX) XXXX-XXXX
    return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 8)}-${cleaned.slice(8)}`;
  }

  return phone;
}

/**
 * Gera link pra abrir conversa no WhatsApp
 */
export function getWhatsAppLink(phone: string, message?: string): string {
  const formatted = formatPhone(phone);
  const encodedMessage = message ? encodeURIComponent(message) : "";
  return `https://wa.me/${formatted}${encodedMessage ? `?text=${encodedMessage}` : ""}`;
}

/**
 * Calcula tempo relativo da última mensagem
 */
export function getLastMessageTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "agora";
  if (minutes < 60) return `${minutes}min atrás`;
  if (hours < 24) return `${hours}h atrás`;
  if (days < 7) return `${days}d atrás`;

  return date.toLocaleDateString("pt-BR");
}

/**
 * Status colors
 */
export const statusColors: Record<string, string> = {
  enviada: "text-gray-400",
  entregue: "text-blue-400",
  lida: "text-green-500",
  erro: "text-red-500",
};

/**
 * Status icons (check marks)
 */
export const statusIcons: Record<string, string> = {
  enviada: "✓",
  entregue: "✓✓",
  lida: "✓✓",
  erro: "✗",
};
