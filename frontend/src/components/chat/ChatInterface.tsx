"use client"

import { useState, useRef, useEffect } from "react"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Trash2 } from "lucide-react"
import { api, ApiError } from "@/lib/api"
import { useChat } from "@/contexts/ChatContext"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  model_used?: string
  response_time?: number
  rag_sources?: Array<{
    title: string
    content: string
    relevance: number
  }>
  rag_confidence?: number
}

/**
 * Composant ChatInterface - Interface de chat principal
 * Gère l'affichage des messages et l'envoi de nouveaux messages
 * Intégré avec l'API backend pour les vraies réponses IA
 */
export function ChatInterface() {
  const { messages, addMessage, clearMessages } = useChat()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ragMode, setRagMode] = useState<'off' | 'hybrid' | 'only'>('hybrid')
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = async (content: string) => {
    // Créer le message utilisateur
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    }

    addMessage(userMessage)
    setIsLoading(true)
    setError(null)

    try {
      // Appel à l'API backend pour obtenir une vraie réponse IA avec RAG
      const response = await api.sendMessage(content, false, ragMode)

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.message,
        isUser: false,
        timestamp: new Date(),
        model_used: response.model_used,
        response_time: response.response_time,
        rag_sources: response.rag_sources,
        rag_confidence: response.rag_confidence
      }

      addMessage(aiMessage)
    } catch (err) {
      console.error('Erreur lors de l\'envoi du message:', err)

      let errorMessage = "Une erreur est survenue lors de la communication avec l'IA."
      if (err instanceof ApiError) {
        errorMessage = `Erreur API: ${err.message}`
      }

      setError(errorMessage)

      // Ajouter un message d'erreur
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        content: `❌ ${errorMessage}`,
        isUser: false,
        timestamp: new Date()
      }
      addMessage(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-scroll vers le bas quand de nouveaux messages arrivent
  // C'est pratique pour suivre la conversation
  useEffect(() => {
    if (scrollAreaRef.current) {
      // Use setTimeout to ensure the DOM has updated
      setTimeout(() => {
        scrollAreaRef.current!.scrollTop = scrollAreaRef.current!.scrollHeight
      }, 100)
    }
  }, [messages])

  return (
    <div className="flex flex-col h-full w-full">
      {/* Header with controls */}
      <div className="flex items-center justify-between p-4 border-b border-border flex-shrink-0 bg-card">
        <h2 className="text-lg font-semibold text-foreground">Chat avec l'IA</h2>
        <div className="flex items-center gap-4">
          {/* Sélecteur mode RAG */}
          <div className="flex items-center gap-3">
            <Label htmlFor="rag-mode" className="text-sm text-muted-foreground whitespace-nowrap">
              Mode RAG:
            </Label>
            <Select value={ragMode} onValueChange={(v) => setRagMode(v as any)}>
              <SelectTrigger id="rag-mode" className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="off">Désactivé</SelectItem>
                <SelectItem value="hybrid">Hybride</SelectItem>
                <SelectItem value="only">RAG uniquement</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            onClick={clearMessages}
            variant="outline"
            size="sm"
            className="text-muted-foreground hover:text-foreground"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Effacer
          </Button>
        </div>
      </div>

      {/* Messages area with scroll */}
      <div
        ref={scrollAreaRef}
        className="flex-1 overflow-y-auto bg-background"
        style={{ minHeight: 0 }}
      >
        <div className="p-4 space-y-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.content}
              isUser={message.isUser}
              timestamp={message.timestamp}
              model_used={message.model_used}
              response_time={message.response_time}
              rag_sources={message.rag_sources}
              rag_confidence={message.rag_confidence}
            />
          ))}
          {/* Animation de typing - les petits points qui bougent */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm flex-shrink-0">
                AI
              </div>
              <div className="bg-card rounded-lg px-4 py-2 border border-border">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input area */}
      <div className="flex-shrink-0 border-t border-border bg-card">
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  )
}
