import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownProps {
  children: string
  className?: string
}

export function Markdown({ children, className = '' }: MarkdownProps) {
  return (
    <ReactMarkdown
      className={`prose prose-invert max-w-none ${className}`}
      remarkPlugins={[remarkGfm]}
      components={{
        // Style des titres
        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-4 text-white" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mb-3 text-white" {...props} />,
        h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mb-2 text-white" {...props} />,

        // Style des tableaux
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full border border-border rounded-md" {...props} />
          </div>
        ),
        th: ({ node, ...props }) => (
          <th className="border border-border bg-muted px-4 py-2 text-left font-semibold" {...props} />
        ),
        td: ({ node, ...props }) => (
          <td className="border border-border px-4 py-2" {...props} />
        ),

        // Style des listes
        ul: ({ node, ...props }) => <ul className="list-disc list-inside my-2 space-y-1" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal list-inside my-2 space-y-1" {...props} />,

        // Style du code
        code: ({ node, inline, ...props }) =>
          inline ? (
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-primary" {...props} />
          ) : (
            <code className="block bg-muted p-4 rounded-md my-2 text-sm font-mono overflow-x-auto" {...props} />
          ),

        // Style des citations
        blockquote: ({ node, ...props }) => (
          <blockquote className="border-l-4 border-primary pl-4 italic my-4 text-muted-foreground" {...props} />
        ),

        // Style des liens
        a: ({ node, ...props }) => (
          <a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />
        ),

        // Style des paragraphes
        p: ({ node, ...props }) => <p className="my-2 leading-relaxed" {...props} />,
      }}
    >
      {children}
    </ReactMarkdown>
  )
}
