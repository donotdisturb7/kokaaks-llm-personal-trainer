"use client"

import { Avatar, AvatarFallback } from "../ui/avatar"
import { cn } from "@/lib/utils"

interface ChatMessageProps {
  message: string
  isUser: boolean
  timestamp?: Date
  model_used?: string
  response_time?: number
}

export function ChatMessage({ message, isUser, timestamp, model_used, response_time }: ChatMessageProps) {
  return (
    <div className={cn(
      "flex gap-3 w-full",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <Avatar className="h-8 w-8 flex-shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground text-sm">
            AI
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={cn(
        "max-w-[70%] rounded-lg px-4 py-3",
        isUser 
          ? "bg-primary text-primary-foreground" 
          : "bg-card text-card-foreground border border-border"
      )}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message}</p>
        <div className="text-xs opacity-70 mt-2 space-y-1">
          {timestamp && (
            <p>{timestamp.toLocaleTimeString()}</p>
          )}
          {!isUser && model_used && (
            <p className="text-primary">🤖 {model_used}</p>
          )}
          {!isUser && response_time && (
            <p className="text-green-400">⚡ {response_time.toFixed(2)}s</p>
          )}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8 flex-shrink-0">
          <AvatarFallback className="bg-secondary text-secondary-foreground text-sm">
            U
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
