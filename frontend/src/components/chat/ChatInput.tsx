"use client"

import { useState } from "react"
import { Send } from "lucide-react"
import { Textarea } from "@/components/ui/Textarea"
import { Button } from "@/components/ui/Button"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

/**
 * Composant ChatInput - Zone de saisie pour le chat
 * Gère l'envoi de messages avec validation
 */
export function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez des questions sur l'entraînement de visée, les exercices ou les techniques..."
            disabled={disabled}
            className="min-h-[44px] max-h-32"
            rows={1}
          />
        </div>
        <Button
          type="submit"
          disabled={!message.trim() || disabled}
          size="sm"
          className="p-3"
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>
    </form>
  )
}
