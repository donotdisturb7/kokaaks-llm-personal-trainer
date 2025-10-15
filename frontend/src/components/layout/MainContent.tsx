"use client"

import { TabsContent } from "@/components/ui/tabs"
import { ChatInterface } from "@/components/chat/ChatInterface"
import ArtifactsTab from "@/components/artifacts/ArtifactsTab"
import PdfUploaderTab from "@/components/rag/PdfUploaderTab"
import { BarChart3, Settings } from "lucide-react"

/**
 * Composant MainContent - Zone de contenu principal
 * Gère l'affichage du contenu selon l'onglet sélectionné
 */
export function MainContent() {
  return (
    <>
      <TabsContent value="chat" className="m-0 flex-1 h-full overflow-hidden data-[state=active]:flex data-[state=active]:flex-col">
        <ChatInterface />
      </TabsContent>

      <TabsContent value="artifacts" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <ArtifactsTab />
      </TabsContent>

      <TabsContent value="pdf" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <PdfUploaderTab />
      </TabsContent>

      <TabsContent value="stats" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">Tableau de Bord</h3>
            <p className="text-muted-foreground">
              Vos statistiques KovaaK's et suivi de progression apparaîtront ici.
            </p>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="settings" className="m-0 flex-1 h-full overflow-auto p-6 data-[state=active]:flex data-[state=active]:flex-col">
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <Settings className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">Paramètres</h3>
            <p className="text-muted-foreground">
              Configurez votre assistant IA et vos préférences d'entraînement.
            </p>
          </div>
        </div>
      </TabsContent>
    </>
  )
}
