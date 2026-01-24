import React, { useCallback, useEffect, useState, useMemo } from 'react'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  Panel,
  NodeTypes,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, RotateCcw, CheckCircle, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import { ConceptNode } from '../components/graph/ConceptNode'
import { NodeInspector } from '../components/graph/NodeInspector'
import { fetchConceptGraph, saveConceptGraph, validateGraph, ValidationResult } from '../api'

// Node types for React Flow
const nodeTypes: NodeTypes = {
  concept: ConceptNode,
}

interface GraphFilters {
  subject: string
  grade: string
  chapter: string
}

const SUBJECTS = ['math', 'science', 'english']
const GRADES = ['5', '6', '7', '8', '9', '10']

export function GraphBuilder() {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState<GraphFilters>({
    subject: 'math',
    grade: '5',
    chapter: 'factors_multiples',
  })
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Fetch graph data
  const { data: graphData, isLoading, error, refetch } = useQuery({
    queryKey: ['concept-graph', filters],
    queryFn: () => fetchConceptGraph(filters.subject, filters.grade, filters.chapter),
    enabled: !!filters.chapter,
  })

  // Validate graph mutation
  const validateMutation = useMutation({
    mutationFn: () => validateGraph(filters.subject, filters.grade, filters.chapter),
    onSuccess: (result: ValidationResult) => {
      if (result.valid) {
        toast.success('Graph is valid! No cycles or issues detected.')
      } else {
        toast.error(`Validation failed: ${result.errors.join(', ')}`)
      }
    },
    onError: () => toast.error('Failed to validate graph'),
  })

  // Save graph mutation
  const saveMutation = useMutation({
    mutationFn: () => saveConceptGraph(filters.subject, filters.grade, filters.chapter, {
      nodes: nodes.map(n => ({
        concept_id: n.id,
        position: n.position,
        ...n.data,
      })),
      edges: edges.map(e => ({
        from: e.source,
        to: e.target,
        kind: e.data?.kind || 'prerequisite',
      })),
    }),
    onSuccess: () => {
      toast.success('Graph saved successfully!')
      setHasUnsavedChanges(false)
      queryClient.invalidateQueries({ queryKey: ['concept-graph', filters] })
    },
    onError: () => toast.error('Failed to save graph'),
  })

  // Transform API data to React Flow format
  useEffect(() => {
    if (graphData) {
      const flowNodes: Node[] = graphData.nodes.map((node: any, index: number) => ({
        id: node.concept_id,
        type: 'concept',
        position: node.position || { x: 250 + (index % 3) * 300, y: 100 + Math.floor(index / 3) * 150 },
        data: {
          label: node.name,
          conceptId: node.concept_id,
          description: node.description,
          bloomTargets: node.bloom_targets || [],
          difficultyDefault: node.difficulty_default || 1,
          templateCount: node.template_count || 0,
          status: node.status || 'draft',
        },
      }))

      const flowEdges: Edge[] = graphData.edges.map((edge: any, index: number) => ({
        id: `e${index}-${edge.from_concept || edge.from}-${edge.to_concept || edge.to}`,
        source: edge.from_concept || edge.from,
        target: edge.to_concept || edge.to,
        type: 'smoothstep',
        animated: edge.kind === 'prerequisite',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: edge.kind === 'prerequisite' ? '#3b82f6' : '#9ca3af',
        },
        style: {
          stroke: edge.kind === 'prerequisite' ? '#3b82f6' : '#9ca3af',
          strokeWidth: 2,
        },
        data: { kind: edge.kind, reason: edge.reason },
      }))

      setNodes(flowNodes)
      setEdges(flowEdges)
      setHasUnsavedChanges(false)
    }
  }, [graphData, setNodes, setEdges])

  // Handle edge connection
  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}`,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#3b82f6',
        },
        style: { stroke: '#3b82f6', strokeWidth: 2 },
        data: { kind: 'prerequisite' },
      } as Edge
      setEdges((eds) => addEdge(newEdge, eds))
      setHasUnsavedChanges(true)
      toast.success('Edge added! Click Save to persist.')
    },
    [setEdges]
  )

  // Handle node click
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  // Handle edge delete
  const onEdgeDelete = useCallback((edgeId: string) => {
    setEdges((eds) => eds.filter((e) => e.id !== edgeId))
    setHasUnsavedChanges(true)
    toast.success('Edge removed!')
  }, [setEdges])

  // Handle node position change
  const onNodeDragStop = useCallback(() => {
    setHasUnsavedChanges(true)
  }, [])

  // Close inspector
  const closeInspector = useCallback(() => {
    setSelectedNode(null)
  }, [])

  // Update node data from inspector
  const updateNodeData = useCallback((nodeId: string, newData: Partial<Node['data']>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...newData } } : node
      )
    )
    setHasUnsavedChanges(true)
  }, [setNodes])

  // Chapters dropdown
  const chapters = useMemo(() => {
    if (filters.subject === 'math' && filters.grade === '5') {
      return [
        { key: 'factors_multiples', name: 'Factors & Multiples' },
        { key: 'fractions', name: 'Fractions' },
        { key: 'decimals', name: 'Decimals' },
      ]
    }
    return [{ key: 'default', name: 'Sample Chapter' }]
  }, [filters.subject, filters.grade])

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Error loading graph data. Please try again.</p>
          <button onClick={() => refetch()} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-64px)] flex">
      {/* Main Graph Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          className="bg-gray-50"
        >
          <Controls />
          <MiniMap
            nodeColor={(n) => {
              if (n.data?.status === 'published') return '#10b981'
              if (n.data?.status === 'review') return '#f59e0b'
              if (n.data?.status === 'no_content') return '#ef4444'
              return '#6b7280'
            }}
            maskColor="rgba(0,0,0,0.1)"
          />
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />

          {/* Top Toolbar */}
          <Panel position="top-left" className="flex gap-2">
            <div className="bg-white rounded-lg shadow-md p-3 flex gap-3 items-center">
              <select
                value={filters.subject}
                onChange={(e) => setFilters({ ...filters, subject: e.target.value })}
                className="border rounded px-2 py-1.5 text-sm"
              >
                {SUBJECTS.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
              <select
                value={filters.grade}
                onChange={(e) => setFilters({ ...filters, grade: e.target.value })}
                className="border rounded px-2 py-1.5 text-sm"
              >
                {GRADES.map((g) => (
                  <option key={g} value={g}>
                    Class {g}
                  </option>
                ))}
              </select>
              <select
                value={filters.chapter}
                onChange={(e) => setFilters({ ...filters, chapter: e.target.value })}
                className="border rounded px-2 py-1.5 text-sm"
              >
                {chapters.map((c) => (
                  <option key={c.key} value={c.key}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          </Panel>

          {/* Action Toolbar */}
          <Panel position="top-right" className="flex gap-2">
            <div className="bg-white rounded-lg shadow-md p-2 flex gap-2">
              <button
                onClick={() => validateMutation.mutate()}
                disabled={validateMutation.isPending}
                className="flex items-center gap-1.5 py-1.5 px-3 text-sm border rounded hover:bg-gray-50"
                title="Validate Graph"
              >
                <CheckCircle className="h-4 w-4" />
                Validate
              </button>
              <button
                onClick={() => saveMutation.mutate()}
                disabled={saveMutation.isPending || !hasUnsavedChanges}
                className={`flex items-center gap-1.5 py-1.5 px-3 text-sm rounded ${
                  hasUnsavedChanges
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
                title="Save Graph"
              >
                <Save className="h-4 w-4" />
                {saveMutation.isPending ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => refetch()}
                className="flex items-center gap-1.5 py-1.5 px-3 text-sm border rounded hover:bg-gray-50"
                title="Reset to saved"
              >
                <RotateCcw className="h-4 w-4" />
                Reset
              </button>
            </div>
          </Panel>

          {/* Status indicator */}
          {hasUnsavedChanges && (
            <Panel position="bottom-right">
              <div className="bg-yellow-100 border border-yellow-300 rounded-lg px-3 py-2 flex items-center gap-2 text-sm text-yellow-800">
                <AlertTriangle className="h-4 w-4" />
                Unsaved changes
              </div>
            </Panel>
          )}

          {/* Legend */}
          <Panel position="bottom-left" className="ml-10">
            <div className="bg-white rounded-lg shadow-md p-3 text-xs">
              <div className="font-semibold mb-2">Legend</div>
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span>Published (≥5 templates)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <span>In Review</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-500"></div>
                  <span>Draft</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span>No Content</span>
                </div>
              </div>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {/* Node Inspector Sidebar */}
      {selectedNode && (
        <NodeInspector
          node={selectedNode}
          onClose={closeInspector}
          onUpdate={updateNodeData}
          edges={edges}
          onDeleteEdge={onEdgeDelete}
        />
      )}
    </div>
  )
}
