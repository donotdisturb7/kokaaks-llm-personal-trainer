"use client"

import { Tabs } from "@/components/ui/tabs"
import { Header } from "./Header"
import { Sidebar } from "./Sidebar"
import { MainContent } from "./MainContent"

/**
 * Composant AppLayout - Layout principal de l'application
 * Structure générale avec header, sidebar et contenu principal
 */
export function AppLayout() {
  return (
    <div className="h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 overflow-hidden">
        <Tabs defaultValue="chat" className="h-full flex">
          <Sidebar />
          <MainContent />
        </Tabs>
      </main>
    </div>
  )
}
