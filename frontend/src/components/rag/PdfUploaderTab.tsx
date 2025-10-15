"use client"

import { useState, useEffect } from "react"
import { Upload, CheckCircle2, AlertCircle, Loader2, FileText, Trash2, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { api, ApiError } from "@/lib/api"

interface Document {
  id: number
  title: string
  source: string
  doc_type: string
  topics: string[]
  safety: string
  created_at: string
}

/**
 * Onglet d'upload de PDF pour le système RAG
 * Permet de téléverser un PDF, définir un titre, des topics et le niveau de sécurité
 */
export default function PdfUploaderTab() {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [topics, setTopics] = useState<string>("")
  const [safety, setSafety] = useState<string>("general")
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<{ document_id: number; chunks_created: number; message: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setIsLoadingDocs(true)
    try {
      const res = await api.listDocuments()
      setDocuments(res.documents)
    } catch (e: any) {
      console.error("Erreur lors du chargement des documents:", e)
    } finally {
      setIsLoadingDocs(false)
    }
  }

  const handleDelete = async (docId: number) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce document ?")) return
    try {
      await api.deleteDocument(docId)
      await fetchDocuments()
    } catch (e: any) {
      setError(e instanceof ApiError ? e.message : "Échec de la suppression")
    }
  }

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResult(null)
    setError(null)
    const f = e.target.files?.[0] || null
    setFile(f)
    if (f && !title) setTitle(f.name.replace(/\.pdf$/i, ""))
  }

  const handleUpload = async () => {
    if (!file) {
      setError("Veuillez sélectionner un fichier PDF")
      return
    }
    setIsUploading(true)
    setError(null)
    setResult(null)
    try {
      const topicsArray = topics
        .split(",")
        .map((t) => t.trim())
        .filter((t) => t.length > 0)
      const res = await api.uploadPDF(file, title || file.name, "pdf", topicsArray, safety)
      setResult(res)
      await fetchDocuments() // Refresh list after upload
    } catch (e: any) {
      if (e instanceof ApiError) setError(e.message)
      else setError("Échec de l'upload. Veuillez réessayer.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Uploader un PDF</h2>
          <p className="text-muted-foreground">Ajoutez vos documents d'entraînement pour l'IA (RAG)</p>
        </div>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            <CardTitle>Téléversement</CardTitle>
          </div>
          <CardDescription>Sélectionnez un PDF et renseignez les métadonnées</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="file">Fichier PDF</Label>
              <Input id="file" type="file" accept="application/pdf" onChange={onFileChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="title">Titre</Label>
              <Input id="title" placeholder="Nom du document" value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="topics">Topics (séparés par des virgules)</Label>
              <Input id="topics" placeholder="wrist, tracking, warmup" value={topics} onChange={(e) => setTopics(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="safety">Niveau de sécurité</Label>
              <select
                id="safety"
                value={safety}
                onChange={(e) => setSafety(e.target.value)}
                className="h-9 px-3 py-2 bg-input border border-border rounded-md text-sm"
              >
                <option value="general">general</option>
                <option value="training">training</option>
                <option value="medical">medical</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex gap-2">
              {topics
                .split(",")
                .map((t) => t.trim())
                .filter((t) => t)
                .slice(0, 5)
                .map((t) => (
                  <Badge key={t} variant="outline" className="text-xs">
                    {t}
                  </Badge>
                ))}
            </div>
            <Button onClick={handleUpload} disabled={!file || isUploading} className="min-w-40">
              {isUploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
              {isUploading ? "Téléversement..." : "Uploader"}
            </Button>
          </div>

          {result && (
            <div className="flex items-center gap-2 text-green-400">
              <CheckCircle2 className="w-5 h-5" />
              <span>
                {result.message} – ID: {result.document_id}, chunks: {result.chunks_created}
              </span>
            </div>
          )}
          {error && (
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Liste des documents */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              <CardTitle>Documents uploadés ({documents.length})</CardTitle>
            </div>
            <Button onClick={fetchDocuments} variant="outline" size="sm" disabled={isLoadingDocs}>
              {isLoadingDocs ? <Loader2 className="w-4 h-4 animate-spin" /> : "Actualiser"}
            </Button>
          </div>
          <CardDescription>Liste des documents ingérés dans le système RAG</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingDocs ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Aucun document uploadé pour le moment</p>
            </div>
          ) : (
            <ScrollArea className="h-96">
              <div className="space-y-3">
                {documents.map((doc) => (
                  <Card key={doc.id} className="bg-card/50 border-border/50">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-primary" />
                            <h4 className="font-semibold text-sm">{doc.title}</h4>
                          </div>
                          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(doc.created_at).toLocaleDateString('fr-FR')}
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {doc.doc_type}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {doc.safety}
                            </Badge>
                          </div>
                          {doc.topics && doc.topics.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {doc.topics.filter(t => t).map((topic, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {topic}
                                </Badge>
                              ))}
                            </div>
                          )}
                          <p className="text-xs text-muted-foreground">Source: {doc.source}</p>
                        </div>
                        <Button
                          onClick={() => handleDelete(doc.id)}
                          variant="ghost"
                          size="sm"
                          className="text-red-400 hover:text-red-300 hover:bg-red-950/20"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


