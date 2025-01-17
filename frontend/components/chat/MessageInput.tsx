import React, { useState } from 'react'

interface MessageInputProps {
  onSendMessage: (message: string) => void;
}

export function MessageInput({ onSendMessage }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      onSendMessage(message)
      setMessage('')
    }
  }

  return (
    <div className="bg-white p-2 shadow-sm">
      <form onSubmit={handleSubmit} className="flex items-center space-x-2">
        {/* Input area */}
        <div className="flex-grow bg-gray-100 rounded-full">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Message"
            className="w-full px-4 py-2 bg-transparent outline-none text-base"
          />
        </div>

        {/* Send button */}
        {message.trim() ? (
          <button 
            type="submit" 
            className="text-blue-500 font-semibold text-base px-3 py-2 rounded-full"
          >
            Send
          </button>
        ) : null}
      </form>
    </div>
  )
}