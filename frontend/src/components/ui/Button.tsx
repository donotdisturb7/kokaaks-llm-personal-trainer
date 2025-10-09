"use client"

import { cn } from "@/lib/utils"
import { ReactNode } from "react"

interface ButtonProps {
  children: ReactNode
  onClick?: () => void
  disabled?: boolean
  variant?: "primary" | "secondary" | "ghost"
  size?: "sm" | "md" | "lg"
  className?: string
  type?: "button" | "submit" | "reset"
}

/**
 * Composant Button - Bouton réutilisable
 * @param variant - Style du bouton (primary, secondary, ghost)
 * @param size - Taille du bouton (sm, md, lg)
 * 
 * NOTE: Utilise cn() pour combiner les classes Tailwind de manière propre
 * TODO: Ajouter plus de variants (success, danger, warning)
 */
export function Button({ 
  children, 
  onClick, 
  disabled = false, 
  variant = "primary", 
  size = "md",
  className,
  type = "button"
}: ButtonProps) {
  // Styles de base pour tous les boutons
  const baseStyles = "inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
  
  // Variants de couleurs - facile d'en ajouter d'autres
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white",
    secondary: "bg-gray-800 hover:bg-gray-700 text-white border border-gray-700",
    ghost: "hover:bg-gray-800 text-gray-300 hover:text-white"
  }
  
  // Tailles disponibles - responsive et cohérentes
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </button>
  )
}
