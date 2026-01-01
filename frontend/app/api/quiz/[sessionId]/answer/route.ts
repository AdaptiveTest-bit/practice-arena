export async function POST(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params
    const body = await request.json()
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(`${baseUrl}/api/quiz/${sessionId}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error('Failed to submit answer')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error submitting answer:', error)
    return Response.json({ error: 'Failed to submit answer' }, { status: 500 })
  }
}
