"use client"

import { MessageCircle, FileText, BarChart3, Settings, Upload } from "lucide-react"
import { TabsList, TabsTrigger } from "@/components/ui/tabs"

/**
 * Composant Sidebar - Barre latérale de navigation
 * Contient les onglets de navigation principaux
 * 
 * NOTE: La largeur est fixée à w-64 (256px) - assez large pour être confortable
 * HACK: Utilise TabsList mais en mode vertical, pas très standard mais ça marche
 */
export function Sidebar() {
  return (
    <TabsList className="flex flex-col w-64 bg-black/20 backdrop-blur-md border-r border-white/10 rounded-none h-full p-0 gap-2 pt-4">
      {/* Onglet Chat */}
      <TabsTrigger
        value="chat"
        className="relative flex items-center gap-3 justify-start px-6 py-3 w-full rounded-none transition-all duration-200 data-[state=active]:bg-white/5 data-[state=active]:text-[hsl(var(--harvest-orange))] hover:bg-white/5 group"
      >
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[hsl(var(--harvest-orange))] opacity-0 transition-opacity data-[state=active]:opacity-100" />
        <MessageCircle className="h-5 w-5 transition-colors group-hover:text-[hsl(var(--harvest-orange))]" />
        <span className="font-medium">Chat</span>
      </TabsTrigger>

      {/* Onglet Artifacts */}
      <TabsTrigger
        value="artifacts"
        className="relative flex items-center gap-3 justify-start px-6 py-3 w-full rounded-none transition-all duration-200 data-[state=active]:bg-white/5 data-[state=active]:text-[hsl(var(--harvest-orange))] hover:bg-white/5 group"
      >
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[hsl(var(--harvest-orange))] opacity-0 transition-opacity data-[state=active]:opacity-100" />
        <FileText className="h-5 w-5 transition-colors group-hover:text-[hsl(var(--harvest-orange))]" />
        <span className="font-medium">Artifacts</span>
      </TabsTrigger>

      {/* Onglet PDF Uploader */}
      <TabsTrigger
        value="pdf"
        className="relative flex items-center gap-3 justify-start px-6 py-3 w-full rounded-none transition-all duration-200 data-[state=active]:bg-white/5 data-[state=active]:text-[hsl(var(--harvest-orange))] hover:bg-white/5 group"
      >
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[hsl(var(--harvest-orange))] opacity-0 transition-opacity data-[state=active]:opacity-100" />
        <Upload className="h-5 w-5 transition-colors group-hover:text-[hsl(var(--harvest-orange))]" />
        <span className="font-medium">PDF Uploader</span>
      </TabsTrigger>

      {/* Onglet Stats */}
      <TabsTrigger
        value="stats"
        className="relative flex items-center gap-3 justify-start px-6 py-3 w-full rounded-none transition-all duration-200 data-[state=active]:bg-white/5 data-[state=active]:text-[hsl(var(--harvest-orange))] hover:bg-white/5 group"
      >
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[hsl(var(--harvest-orange))] opacity-0 transition-opacity data-[state=active]:opacity-100" />
        <BarChart3 className="h-5 w-5 transition-colors group-hover:text-[hsl(var(--harvest-orange))]" />
        <span className="font-medium">Statistiques</span>
      </TabsTrigger>

      {/* Onglet Paramètres */}
      <TabsTrigger
        value="settings"
        className="relative flex items-center gap-3 justify-start px-6 py-3 w-full rounded-none transition-all duration-200 data-[state=active]:bg-white/5 data-[state=active]:text-[hsl(var(--harvest-orange))] hover:bg-white/5 group"
      >
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[hsl(var(--harvest-orange))] opacity-0 transition-opacity data-[state=active]:opacity-100" />
        <Settings className="h-5 w-5 transition-colors group-hover:text-[hsl(var(--harvest-orange))]" />
        <span className="font-medium">Paramètres</span>
      </TabsTrigger>
    </TabsList>
  )
}
