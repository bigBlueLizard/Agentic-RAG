'use client'
import { SetStateAction, useState } from 'react'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LLMSelector } from '../LLMSelector'
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription, 
    DialogFooter 
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface Message {
    id: number;
    text: string | object;
    sender: 'user' | 'bot';
    delivered?: boolean;
}

function formatObject(obj: any): string {
    if (typeof obj !== 'object' || obj === null) return String(obj)

    return Object.entries(obj)
        .map(([key, value]) => `${key}: ${formatObject(value)}`)
        .join('\n')
}

export function Chat() {
    const [messages, setMessages] = useState<Message[]>([])
    const [apiBase, setApiBase] = useState('http://127.0.0.1:8000/')
    const [requestHeaders, setRequestHeaders] = useState('{}')
    const [systemPrompt, setSystemPrompt] = useState('')
    const [selectedLLM, setSelectedLLM] = useState('gemma agents')
    const [isLoading, setIsLoading] = useState(false)
    
    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false)
    const [pendingMessage, setPendingMessage] = useState<string | null>(null)

    const handleLLMChange = (llm: string) => {
        setSelectedLLM(llm);
    };

    const handleSendMessage = async (text: string, approvalBypass = false) => {
        // Create new user message
        const newMessage: Message = { id: Date.now(), text, sender: 'user' }
        setMessages(prevMessages => [...prevMessages, newMessage])
        
        setIsLoading(true)

        try {
            // Parse headers from textarea
            let headers: Record<string, string> = {}
            try {
                headers = JSON.parse(requestHeaders)
            } catch (error) {
                console.error('Invalid JSON in headers:', error)
                const errorMessage: Message = {
                    id: Date.now() + 1,
                    text: 'Error: Invalid JSON in headers',
                    sender: 'bot'
                }
                setMessages(prevMessages => [...prevMessages, errorMessage])
                setIsLoading(false)
                return
            }

            // Construct URL with encoded query parameters
            const url = new URL('http://127.0.0.1:5000/query/retrieve')
            url.searchParams.set('API_BASE', apiBase)
            url.searchParams.set('query', text)
            url.searchParams.set('system_prompt', systemPrompt)
            
            // Add approval bypass parameter if applicable
            if (approvalBypass) {
                url.searchParams.set('approval_bypass', 'true')
            }

            // Send POST request
            const response = await fetch(url.toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: requestHeaders
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()

            // Check if approval is required
            if (data.approval_required && !approvalBypass) {
                // Open approval modal and store the message
                setPendingMessage(text)
                setIsApprovalModalOpen(true)
                setIsLoading(false)
                return
            }

            // Add bot response to messages
            const botMessage: Message = {
                id: Date.now() + 1,
                text: data.rag_response || 'No RAG response available',
                sender: 'bot'
            }
            setMessages(prevMessages => [...prevMessages, botMessage])

        } catch (error) {
            console.error('Error sending message:', error)

            const errorMessage: Message = {
                id: Date.now() + 1,
                text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                sender: 'bot'
            }
            setMessages(prevMessages => [...prevMessages, errorMessage])

        } finally {
            setIsLoading(false)
        }
    }

    const handleApproval = (approved: boolean) => {
        setIsApprovalModalOpen(false)
        
        if (approved && pendingMessage) {
            // Remove the previous user message before resending
            setMessages(prevMessages => 
                prevMessages.filter(msg => msg.text !== pendingMessage)
            )
            
            // Resend the message with approval bypass
            handleSendMessage(pendingMessage, true)
        }
        
        // Clear the pending message
        setPendingMessage(null)
    }

    return (
        <>
            <Card className="w-full mx-auto">
                <CardHeader>
                    <CardTitle>Chat</CardTitle>
                    <div className="mt-2 flex space-x-4">
                        <div className="flex-1">
                            <Label htmlFor="apiBase">API Base URL</Label>
                            <Input
                                id="apiBase"
                                placeholder="Enter API Base URL"
                                value={apiBase}
                                onChange={(e) => setApiBase(e.target.value)}
                                className="mt-1"
                            />
                            <div className="">
                                <Label>Configuration</Label>
                                <LLMSelector
                                    selectedLLM={selectedLLM}
                                    onLLMChange={handleLLMChange}
                                />
                            </div>
                        </div>
                        <div className="flex-1">
                            <Label htmlFor="requestHeaders">Request Headers (JSON)</Label>
                            <Textarea
                                id="requestHeaders"
                                placeholder="Enter JSON request headers"
                                value={requestHeaders}
                                onChange={(e: { target: { value: SetStateAction<string> } }) => setRequestHeaders(e.target.value)}
                                className="mt-1"
                                rows={4}
                            />
                        </div>
                        <div className="flex-1">
                            <Label htmlFor="systemPrompt">System Prompt</Label>
                            <Textarea
                                id="systemPrompt"
                                placeholder="Enter system prompt to guide the AI's behavior"
                                value={systemPrompt}
                                onChange={(e: { target: { value: SetStateAction<string> } }) => setSystemPrompt(e.target.value)}
                                className="mt-1"
                                rows={4}
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <MessageList 
                        messages={messages} 
                        isLoading={isLoading}
                    />
                    <div className="mt-4">
                        <MessageInput onSendMessage={handleSendMessage} />
                    </div>
                </CardContent>
            </Card>

            {/* Approval Modal */}
            <Dialog open={isApprovalModalOpen} onOpenChange={() => setIsApprovalModalOpen(false)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Approval Required</DialogTitle>
                        <DialogDescription>
                            Are you sure you want the AI to take this action on your behalf?
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => handleApproval(false)}>
                            No, Cancel
                        </Button>
                        <Button onClick={() => handleApproval(true)}>
                            Yes, Proceed
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    )
}