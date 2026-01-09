export async function GET(
  request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(`${baseUrl}/api/quiz/${sessionId}/question`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch question')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error fetching question:', error)
    return Response.json({ error: 'Failed to fetch question' }, { status: 500 })
  }
}
