import React, { memo } from 'react'
import { Handle, Position, NodeProps } from '@xyflow/react'
import { FileText, AlertCircle } from 'lucide-react'

interface ConceptNodeData {
  label: string
  conceptId: string
  description?: string
  bloomTargets: string[]
  difficultyDefault: number
  templateCount: number
  status: 'draft' | 'review' | 'published' | 'no_content'
}

function ConceptNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as unknown as ConceptNodeData

  const getStatusColor = () => {
    switch (nodeData.status) {
      case 'published':
        return 'border-green-500 bg-green-50'
      case 'review':
        return 'border-yellow-500 bg-yellow-50'
      case 'draft':
        return 'border-gray-400 bg-gray-50'
      case 'no_content':
        return 'border-red-500 bg-red-50'
      default:
        return 'border-gray-300 bg-white'
    }
  }

  const getStatusBadge = () => {
    switch (nodeData.status) {
      case 'published':
        return <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded">✓ Published</span>
      case 'review':
        return <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">⏳ Review</span>
      case 'draft':
        return <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded">Draft</span>
      case 'no_content':
        return <span className="text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded">⚠ No Content</span>
      default:
        return null
    }
  }

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 shadow-md min-w-[180px] max-w-[220px]
        transition-all duration-200
        ${getStatusColor()}
        ${selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
      `}
    >
      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-blue-500 border-2 border-white"
      />

      {/* Node content */}
      <div className="flex flex-col gap-1.5">
        {/* Header with name */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-sm text-gray-900 leading-tight">
            {nodeData.label}
          </h3>
          {nodeData.status === 'no_content' && (
            <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
          )}
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-2">
          {getStatusBadge()}
        </div>

        {/* Template count */}
        <div className="flex items-center gap-1.5 text-xs text-gray-600">
          <FileText className="h-3 w-3" />
          <span>{nodeData.templateCount} templates</span>
        </div>

        {/* Bloom targets */}
        {nodeData.bloomTargets && nodeData.bloomTargets.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {nodeData.bloomTargets.slice(0, 2).map((bloom) => (
              <span
                key={bloom}
                className="text-[9px] bg-blue-100 text-blue-700 px-1 py-0.5 rounded"
              >
                {bloom}
              </span>
            ))}
            {nodeData.bloomTargets.length > 2 && (
              <span className="text-[9px] text-gray-500">
                +{nodeData.bloomTargets.length - 2}
              </span>
            )}
          </div>
        )}

        {/* Difficulty indicator */}
        <div className="flex items-center gap-1">
          {[1, 2, 3].map((level) => (
            <div
              key={level}
              className={`h-1.5 w-4 rounded ${
                level <= nodeData.difficultyDefault
                  ? 'bg-blue-500'
                  : 'bg-gray-200'
              }`}
            />
          ))}
          <span className="text-[9px] text-gray-500 ml-1">
            Tier {nodeData.difficultyDefault}
          </span>
        </div>
      </div>

      {/* Output handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-blue-500 border-2 border-white"
      />
    </div>
  )
}

export const ConceptNode = memo(ConceptNodeComponent)
