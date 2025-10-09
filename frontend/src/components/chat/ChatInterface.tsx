"use client"

import { useState, useRef, useEffect } from "react"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

/**
 * Composant ChatInterface - Interface de chat principal
 * Gère l'affichage des messages et l'envoi de nouveaux messages
 * 
 * TODO: Intégrer avec l'API Ollama pour les vraies réponses IA
 * FIXME: L'animation de typing pourrait être plus fluide
 * NOTE: Pour l'instant c'est juste une simulation, mais ça donne une bonne idée
 */
export function ChatInterface() {
  // Messages initiaux - on commence avec un message de bienvenue
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Salut ! Je suis ton assistant IA pour l'entraînement de visée. Je peux t'aider avec des exercices, techniques et conseils personnalisés. Que veux-tu savoir ?",
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = async (content: string) => {
    // Créer le message utilisateur
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    // Simulation de réponse IA - à remplacer par un vrai appel API
    // TODO: Remplacer par l'intégration Ollama
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Je comprends que tu demandes des conseils d'entraînement. C'est une réponse simulée pour l'instant. Dans la vraie implémentation, ça se connecterait à ton LLM fine-tuné via Ollama.",
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
      setIsLoading(false)
    }, 1000)
  }

  // Auto-scroll vers le bas quand de nouveaux messages arrivent
  // C'est pratique pour suivre la conversation
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="flex flex-col h-full">
      <ScrollArea ref={scrollAreaRef} className="flex-1">
        <div className="space-y-1">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.content}
              isUser={message.isUser}
              timestamp={message.timestamp}
            />
          ))}
          {/* Animation de typing - les petits points qui bougent */}
          {isLoading && (
            <div className="flex gap-3 p-4">
              <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm">
                AI
              </div>
              <div className="bg-gray-800 rounded-lg px-4 py-2 border border-gray-700">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  )
}
