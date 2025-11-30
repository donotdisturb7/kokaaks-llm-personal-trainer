"use client"

import { Avatar, AvatarFallback } from "../ui/avatar"
import { cn } from "@/lib/utils"
import { Markdown } from "@/components/ui/markdown"
import { FileText, TrendingUp } from "lucide-react"

interface Source {
  title: string
  content: string
  relevance: number
}

interface ChatMessageProps {
  message: string
  isUser: boolean
  timestamp?: Date
  model_used?: string
  response_time?: number
  rag_sources?: Source[]
  rag_confidence?: number
}

export function ChatMessage({ message, isUser, timestamp, model_used, response_time, rag_sources, rag_confidence }: ChatMessageProps) {
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
        {/* Contenu du message */}
        <div className="text-sm leading-relaxed">
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message}</p>
          ) : (
            <Markdown>{message}</Markdown>
          )}
        </div>

        {/* Sources RAG (si disponibles) */}
        {!isUser && rag_sources && rag_sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border/50">
            <div className="flex items-center gap-2 mb-2 text-xs text-muted-foreground">
              <FileText className="w-4 h-4" />
              <span>Sources ({rag_sources.length})</span>
              {rag_confidence && (
                <span className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {(rag_confidence * 100).toFixed(0)}% confiance
                </span>
              )}
            </div>
            <div className="space-y-2">
              {rag_sources.map((source, idx) => (
                <div key={idx} className="bg-muted/30 rounded-md p-3 text-xs">
                  <div className="font-semibold text-primary mb-1">{source.title}</div>
                  <div className="text-muted-foreground line-clamp-2">{source.content}</div>
                  <div className="text-xs mt-1 opacity-60">
                    Pertinence: {(source.relevance * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Métadonnées */}
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
