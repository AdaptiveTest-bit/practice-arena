export async function POST(
  request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(`${baseUrl}/api/quiz/${sessionId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to end session')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error ending session:', error)
    return Response.json({ error: 'Failed to end session' }, { status: 500 })
  }
}
