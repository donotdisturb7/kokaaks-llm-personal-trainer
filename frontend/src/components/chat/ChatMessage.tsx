"use client"

import { Avatar, AvatarFallback } from "../ui/avatar"
import { cn } from "@/lib/utils"

interface ChatMessageProps {
  message: string
  isUser: boolean
  timestamp?: Date
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  return (
    <div className={cn(
      "flex gap-3 p-4 message-enter",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-blue-600 text-white text-sm">
            AI
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={cn(
        "max-w-[80%] rounded-lg px-4 py-2",
        isUser 
          ? "bg-blue-600 text-white" 
          : "bg-gray-800 text-gray-100 border border-gray-700"
      )}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
        {timestamp && (
          <p className="text-xs opacity-70 mt-1">
            {timestamp.toLocaleTimeString()}
          </p>
        )}
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-gray-600 text-white text-sm">
            U
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
