import { useQuery } from 'react-query'
import api from '../services/api'
import { format } from 'date-fns'

export default function Outreach() {
  const { data, isLoading } = useQuery('outreach', async () => {
    const response = await api.get('/api/outreach/messages/')
    return response.data
  })

  if (isLoading) return <div className="text-center py-12">Loading...</div>

  const messages = data?.results || []

  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      sent: 'bg-blue-100 text-blue-800',
      delivered: 'bg-green-100 text-green-800',
      opened: 'bg-yellow-100 text-yellow-800',
      responded: 'bg-green-100 text-green-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Outreach</h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage your outreach messages to prospects
        </p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {messages.map((message) => (
            <li key={message.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-gray-900">
                      {message.recipient_email}
                    </p>
                    <span
                      className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        message.status
                      )}`}
                    >
                      {message.status}
                    </span>
                  </div>
                  <div className="mt-1">
                    <p className="text-sm text-gray-600">{message.subject}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Project: {message.project?.title}
                    </p>
                  </div>
                </div>
                <div className="ml-5 text-sm text-gray-500">
                  {message.sent_at
                    ? format(new Date(message.sent_at), 'MMM d, yyyy')
                    : 'Not sent'}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
