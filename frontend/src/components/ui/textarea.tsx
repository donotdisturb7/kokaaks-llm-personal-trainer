"use client"

import { cn } from "@/lib/utils"
import { forwardRef } from "react"

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

/**
 * Composant Textarea - Zone de texte réutilisable
 * @param label - Label optionnel pour le champ
 * @param error - Message d'erreur optionnel
 */
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        <textarea
          className={cn(
            "flex min-h-[80px] w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 resize-none",
            error && "border-red-500 focus:ring-red-500",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
      </div>
    )
  }
)

Textarea.displayName = "Textarea"
