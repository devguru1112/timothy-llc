import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function Verification() {
  const { user, fetchUser } = useAuth()
  const navigate = useNavigate()
  const [phoneCode, setPhoneCode] = useState('')
  const [emailCode, setEmailCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/login')
    }
  }, [user, navigate])

  const sendPhoneCode = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.post('/api/auth/verify/phone/send/')
      setMessage(response.data.message)
      if (response.data.code) {
        setMessage(`Code sent! (Debug mode: ${response.data.code})`)
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to send code')
    } finally {
      setLoading(false)
    }
  }

  const verifyPhone = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.post('/api/auth/verify/phone/', { code: phoneCode })
      setMessage(response.data.message)
      await fetchUser()
      setPhoneCode('')
    } catch (error) {
      setError(error.response?.data?.error || 'Invalid code')
    } finally {
      setLoading(false)
    }
  }

  const sendEmailCode = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.post('/api/auth/verify/email/send/')
      setMessage(response.data.message)
      if (response.data.code) {
        setMessage(`Code sent! (Debug mode: ${response.data.code})`)
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to send code')
    } finally {
      setLoading(false)
    }
  }

  const verifyEmail = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.post('/api/auth/verify/email/', { code: emailCode })
      setMessage(response.data.message)
      await fetchUser()
      setEmailCode('')
    } catch (error) {
      setError(error.response?.data?.error || 'Invalid code')
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return null
  }

  const isFullyVerified = user.phone_verified && user.email_verified

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Verify Your Account</h2>
          
          {isFullyVerified ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-green-800 font-medium">✓ Your account is fully verified!</p>
              <p className="text-sm text-green-600 mt-1">You can now access all job opportunities.</p>
              <button
                onClick={() => navigate('/')}
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Go to Dashboard
              </button>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <p className="text-yellow-800 font-medium">Please verify your phone and email to access all job opportunities.</p>
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          {message && (
            <div className="mb-4 rounded-md bg-blue-50 p-4">
              <div className="text-sm text-blue-800">{message}</div>
            </div>
          )}

          {/* Phone Verification */}
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Phone Verification
              {user.phone_verified && (
                <span className="ml-2 text-green-600">✓ Verified</span>
              )}
            </h3>
            
            {user.phone ? (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">Phone: {user.phone}</p>
                
                {!user.phone_verified && (
                  <>
                    <div className="flex gap-2">
                      <button
                        onClick={sendPhoneCode}
                        disabled={loading}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm disabled:opacity-50"
                      >
                        Send Code
                      </button>
                    </div>
                    
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={phoneCode}
                        onChange={(e) => setPhoneCode(e.target.value)}
                        placeholder="Enter 6-digit code"
                        maxLength={6}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button
                        onClick={verifyPhone}
                        disabled={loading || !phoneCode}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                      >
                        Verify
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No phone number set. Please update your profile.</p>
            )}
          </div>

          {/* Email Verification */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Email Verification
              {user.email_verified && (
                <span className="ml-2 text-green-600">✓ Verified</span>
              )}
            </h3>
            
            <div className="space-y-4">
              <p className="text-sm text-gray-600">Email: {user.email}</p>
              
              {!user.email_verified && (
                <>
                  <div className="flex gap-2">
                    <button
                      onClick={sendEmailCode}
                      disabled={loading}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm disabled:opacity-50"
                    >
                      Send Code
                    </button>
                  </div>
                  
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={emailCode}
                      onChange={(e) => setEmailCode(e.target.value)}
                      placeholder="Enter 6-digit code"
                      maxLength={6}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    <button
                      onClick={verifyEmail}
                      disabled={loading || !emailCode}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      Verify
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
