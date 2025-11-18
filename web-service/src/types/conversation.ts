// 消息類型定義
export interface Message {
  id: string;
  conversationId: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: number;
  status: 'sending' | 'sent' | 'error';
  metadata?: {
    category?: string;
    confidence?: number;
  }
}

// 對話進度階段
export type ConversationStage = 'greeting' | 'assessment' | 'clarification' | 'summary' | 'complete';

// 對話進度
export interface ConversationProgress {
  current: number;              // 0-100
  stage: ConversationStage;
  description: string;
}

// Agent 狀態
export type AgentStatus = 'idle' | 'typing' | 'analyzing';

// Agent 信息
export interface Agent {
  name: string;
  avatar: string;
  status: AgentStatus;
}

// 對話會話
export interface Conversation {
  id: string;
  projectId: string;
  messages: Message[];
  agent: Agent;
  progress: ConversationProgress;
  metadata: {
    startedAt: number;
    updatedAt: number;
    estimatedCompletionTime?: number;
  }
}

// 對話狀態
export interface ConversationState {
  conversation: Conversation | null;
  loading: boolean;
  error: string | null;
  isConnected: boolean;
}

// API 響應類型
export interface InitConversationResponse {
  conversationId: string;
  agent: Agent;
  initialMessage: string;
  timestamp: number;
}

export interface MessageChunkEvent {
  chunk: string;
  isComplete: boolean;
  metadata?: {
    stage?: ConversationStage;
    progress?: number;
  }
}

export interface CompleteConversationResponse {
  summary: string;
  briefing: {
    project_id: string;
    user_profile: Record<string, any>;
    style_preferences: string[];
    key_requirements: string[];
  }
  analysis: Record<string, any>;
}
