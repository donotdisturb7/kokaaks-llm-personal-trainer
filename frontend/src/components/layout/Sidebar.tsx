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
    <TabsList className="flex flex-col w-64 bg-card border-r border-border rounded-none h-full p-0 gap-0">
      {/* Onglet Chat - le plus utilisé probablement */}
      <TabsTrigger 
        value="chat" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full rounded-none data-[state=active]:bg-accent data-[state=active]:text-accent-foreground hover:bg-accent/50"
      >
        <MessageCircle className="h-5 w-5" />
        Chat
      </TabsTrigger>
      
      {/* Onglet Artifacts - feuilles générées par l'IA */}
      <TabsTrigger 
        value="artifacts" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full rounded-none data-[state=active]:bg-accent data-[state=active]:text-accent-foreground hover:bg-accent/50"
      >
        <FileText className="h-5 w-5" />
        Artifacts
      </TabsTrigger>

      {/* Onglet PDF Uploader */}
      <TabsTrigger 
        value="pdf" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full rounded-none data-[state=active]:bg-accent data-[state=active]:text-accent-foreground hover:bg-accent/50"
      >
        <Upload className="h-5 w-5" />
        PDF Uploader
      </TabsTrigger>
      
      {/* Onglet Stats - pour voir les progrès */}
      <TabsTrigger 
        value="stats" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full rounded-none data-[state=active]:bg-accent data-[state=active]:text-accent-foreground hover:bg-accent/50"
      >
        <BarChart3 className="h-5 w-5" />
        Statistiques
      </TabsTrigger>
      
      {/* Onglet Paramètres - configuration de l'IA */}
      <TabsTrigger 
        value="settings" 
        className="flex items-center gap-3 justify-start px-4 py-3 w-full rounded-none data-[state=active]:bg-accent data-[state=active]:text-accent-foreground hover:bg-accent/50"
      >
        <Settings className="h-5 w-5" />
        Paramètres
      </TabsTrigger>
    </TabsList>
  )
}
