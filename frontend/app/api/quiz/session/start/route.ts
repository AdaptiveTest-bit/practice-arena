export async function POST(request: Request) {
  try {
    const body = await request.json()
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(`${baseUrl}/api/quiz/session/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error('Failed to start session')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error starting session:', error)
    return Response.json({ error: 'Failed to start session' }, { status: 500 })
  }
}
