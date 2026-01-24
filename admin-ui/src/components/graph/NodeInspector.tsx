import React, { useState, useEffect } from 'react'
import { Node, Edge } from '@xyflow/react'
import { X, Trash2, Link2, ExternalLink, FileText } from 'lucide-react'

interface NodeInspectorProps {
  node: Node
  onClose: () => void
  onUpdate: (nodeId: string, data: Partial<Node['data']>) => void
  edges: Edge[]
  onDeleteEdge: (edgeId: string) => void
}

const BLOOM_LEVELS = ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']

export function NodeInspector({ node, onClose, onUpdate, edges, onDeleteEdge }: NodeInspectorProps) {
  const nodeData = node.data as Record<string, unknown>
  const [localData, setLocalData] = useState({
    label: (nodeData.label as string) || '',
    description: (nodeData.description as string) || '',
    difficultyDefault: (nodeData.difficultyDefault as number) || 1,
    bloomTargets: (nodeData.bloomTargets as string[]) || [],
  })

  // Reset local state when node changes
  useEffect(() => {
    setLocalData({
      label: (nodeData.label as string) || '',
      description: (nodeData.description as string) || '',
      difficultyDefault: (nodeData.difficultyDefault as number) || 1,
      bloomTargets: (nodeData.bloomTargets as string[]) || [],
    })
  }, [node.id])

  const handleSave = () => {
    onUpdate(node.id, localData)
  }

  const toggleBloomLevel = (level: string) => {
    setLocalData((prev) => ({
      ...prev,
      bloomTargets: prev.bloomTargets.includes(level)
        ? prev.bloomTargets.filter((l) => l !== level)
        : [...prev.bloomTargets, level],
    }))
  }

  // Find edges connected to this node
  const incomingEdges = edges.filter((e) => e.target === node.id)
  const outgoingEdges = edges.filter((e) => e.source === node.id)

  const templateCount = (nodeData.templateCount as number) || 0
  const conceptId = (nodeData.conceptId as string) || node.id

  return (
    <div className="w-80 bg-white border-l border-gray-200 shadow-lg overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">Node Inspector</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded"
        >
          <X className="h-5 w-5 text-gray-500" />
        </button>
      </div>

      <div className="p-4 space-y-6">
        {/* Concept ID (read-only) */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Concept ID
          </label>
          <div className="text-sm font-mono bg-gray-50 p-2 rounded border text-gray-700 break-all">
            {conceptId}
          </div>
        </div>

        {/* Name */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Name
          </label>
          <input
            type="text"
            value={localData.label}
            onChange={(e) => setLocalData({ ...localData, label: e.target.value })}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Description
          </label>
          <textarea
            value={localData.description}
            onChange={(e) => setLocalData({ ...localData, description: e.target.value })}
            rows={3}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>

        {/* Difficulty */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-2">
            Difficulty Tier
          </label>
          <div className="flex gap-2">
            {[1, 2, 3].map((tier) => (
              <button
                key={tier}
                onClick={() => setLocalData({ ...localData, difficultyDefault: tier })}
                className={`flex-1 py-2 rounded text-sm font-medium ${
                  localData.difficultyDefault === tier
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Tier {tier}
              </button>
            ))}
          </div>
        </div>

        {/* Bloom Levels */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-2">
            Bloom's Taxonomy Targets
          </label>
          <div className="flex flex-wrap gap-2">
            {BLOOM_LEVELS.map((level) => (
              <button
                key={level}
                onClick={() => toggleBloomLevel(level)}
                className={`px-2 py-1 rounded text-xs font-medium ${
                  localData.bloomTargets.includes(level)
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Template Stats */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Templates</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{templateCount}</div>
          <p className="text-xs text-gray-500 mt-1">
            {templateCount >= 5 ? '✓ Ready for publishing' : `Need ${5 - templateCount} more for publishing`}
          </p>
          <a
            href={`/templates?concept=${conceptId}`}
            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline mt-2"
          >
            View templates <ExternalLink className="h-3 w-3" />
          </a>
        </div>

        {/* Prerequisites (incoming edges) */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link2 className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              Prerequisites ({incomingEdges.length})
            </span>
          </div>
          {incomingEdges.length === 0 ? (
            <p className="text-xs text-gray-500 italic">No prerequisites (entry point)</p>
          ) : (
            <div className="space-y-2">
              {incomingEdges.map((edge) => (
                <div
                  key={edge.id}
                  className="flex items-center justify-between bg-gray-50 rounded px-2 py-1.5"
                >
                  <span className="text-xs text-gray-700 truncate flex-1">
                    {edge.source.split('.').pop()}
                  </span>
                  <button
                    onClick={() => onDeleteEdge(edge.id)}
                    className="p-1 hover:bg-red-100 rounded text-red-500"
                    title="Remove edge"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Dependents (outgoing edges) */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link2 className="h-4 w-4 text-gray-500 rotate-180" />
            <span className="text-sm font-medium text-gray-700">
              Dependents ({outgoingEdges.length})
            </span>
          </div>
          {outgoingEdges.length === 0 ? (
            <p className="text-xs text-gray-500 italic">No dependents (leaf node)</p>
          ) : (
            <div className="space-y-2">
              {outgoingEdges.map((edge) => (
                <div
                  key={edge.id}
                  className="flex items-center justify-between bg-gray-50 rounded px-2 py-1.5"
                >
                  <span className="text-xs text-gray-700 truncate flex-1">
                    {edge.target.split('.').pop()}
                  </span>
                  <button
                    onClick={() => onDeleteEdge(edge.id)}
                    className="p-1 hover:bg-red-100 rounded text-red-500"
                    title="Remove edge"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="pt-2">
          <button
            onClick={handleSave}
            className="w-full py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}
