"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  model_used?: string
  response_time?: number
}

interface ChatContextType {
  messages: Message[]
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  clearMessages: () => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

interface ChatProviderProps {
  children: ReactNode
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize messages after hydration to avoid SSR mismatch
  useEffect(() => {
    if (!isInitialized) {
      setMessages([
        {
          id: "1",
          content: "Salut ! Je suis ton assistant IA AIM TRAINING, KovaaK's. Je peux t'aider avec des exercices, techniques et conseils personnalisés. Que veux-tu savoir ?",
          isUser: false,
          timestamp: new Date()
        }
      ])
      setIsInitialized(true)
    }
  }, [isInitialized])

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message])
  }

  const clearMessages = () => {
    setMessages([
      {
        id: "1",
        content: "Salut ! Je suis ton assistant IA AIM TRAINING, KovaaK's. Je peux t'aider avec des exercices, techniques et conseils personnalisés. Que veux-tu savoir ?",
        isUser: false,
        timestamp: new Date()
      }
    ])
  }

  return (
    <ChatContext.Provider value={{
      messages,
      setMessages,
      addMessage,
      clearMessages
    }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}
