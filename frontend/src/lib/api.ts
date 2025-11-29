/**
 * API service for communicating with the KovaaK's AI Trainer backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'

export interface ChatMessage {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  model_used?: string
  response_time?: number
}

export interface ChatResponse {
  message: string
  model_used: string
  response_time: number
}

export interface ConversationResponse {
  id: string
  title: string
  messages: Array<{
    id: string
    content: string
    is_user: boolean
    created_at: string
  }>
  created_at: string
  updated_at: string
}

export interface HealthResponse {
  status: string
  llm_provider: string
  database_configured: boolean
  redis_configured: boolean
  kovaaks_username_configured: boolean
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If we can't parse the error, use the default message
    }
    throw new ApiError(errorMessage, response.status)
  }

  return response.json()
}

export const api = {
  /**
   * Check if the backend is healthy
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`)
    return handleResponse<HealthResponse>(response)
  },

  /**
   * Send a chat message and get AI response
   */
  async sendMessage(message: string, includeUserContext: boolean = false): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        include_user_context: includeUserContext,
      }),
    })
    return handleResponse<ChatResponse>(response)
  },

  /**
   * Get conversation history
   */
  async getConversations(): Promise<ConversationResponse[]> {
    const response = await fetch(`${API_BASE_URL}/api/chat/conversation`)
    return handleResponse<ConversationResponse[]>(response)
  },

  /**
   * Get a specific conversation by ID
   */
  async getConversation(id: string): Promise<ConversationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat/conversation/${id}`)
    return handleResponse<ConversationResponse>(response)
  },

  /**
   * Get available LLM models
   */
  async getModels(): Promise<{ models: string[]; default_model: string; provider: string }> {
    const response = await fetch(`${API_BASE_URL}/api/chat/models`)
    return handleResponse<{ models: string[]; default_model: string; provider: string }>(response)
  },

  /**
   * RAG query for document-based responses
   */
  async queryRAG(
    query: string,
    maxResults: number = 5,
    topics?: string[],
    safetyLevel: string = 'general'
  ): Promise<{
    answer: string
    sources: Array<{
      title: string
      chunk: string
      relevance: number
    }>
    confidence: number
  }> {
    const response = await fetch(`${API_BASE_URL}/api/rag/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_results: maxResults,
        topics,
        safety_level: safetyLevel,
      }),
    })
    return handleResponse(response)
  },

  /**
   * Upload a PDF document for RAG
   */
  async uploadPDF(
    file: File,
    title: string,
    docType: string = 'document',
    topics: string[] = [],
    safety: string = 'general'
  ): Promise<{
    document_id: number
    chunks_created: number
    message: string
  }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('doc_type', docType)
    formData.append('topics', topics.join(','))
    formData.append('safety', safety)

    const response = await fetch(`${API_BASE_URL}/api/rag/ingest/pdf`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  /**
   * Get RAG health status
   */
  async getRAGHealth(): Promise<{
    status: string
    embedding_service: string
    vector_dimension: number
  }> {
    const response = await fetch(`${API_BASE_URL}/api/rag/health`)
    return handleResponse(response)
  },

  /**
   * List uploaded RAG documents
   */
  async listDocuments(docType?: string, topics?: string[]): Promise<{
    documents: Array<{
      id: number
      title: string
      source: string
      doc_type: string
      topics: string[]
      safety: string
      created_at: string
    }>
  }> {
    let url = `${API_BASE_URL}/api/rag/documents`
    const params = new URLSearchParams()
    if (docType) params.append('doc_type', docType)
    if (topics && topics.length > 0) {
      topics.forEach(t => params.append('topics', t))
    }
    if (params.toString()) url += `?${params.toString()}`
    
    const response = await fetch(url)
    return handleResponse(response)
  },

  /**
   * Delete a RAG document
   */
  async deleteDocument(documentId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/rag/documents/${documentId}`, {
      method: 'DELETE',
    })
    return handleResponse(response)
  },
}

export { ApiError }
