import { ScrollArea } from "@/components/ui/scroll-area"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useEffect, useRef, useState } from 'react'
// import { MetricsDialog } from './MetricsDialog'
import axios from 'axios'
import { MetricsDialog } from "./MetricsDialog"

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

const TypingIndicator = () => (
  <div className="flex justify-start">
    <div className="bg-muted rounded-2xl px-4 py-3">
      <div className="flex space-x-2">
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" />
      </div>
    </div>
  </div>
);

export function MessageList({ messages, isLoading = false }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [metricsDialogOpen, setMetricsDialogOpen] = useState(false);
  const [selectedMetrics, setSelectedMetrics] = useState(null);
  
  useEffect(() => {
    const scrollElement = scrollRef.current;
    if (scrollElement) {
      scrollElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, isLoading]);

  const handleBotMessageClick = async (messageIndex: number) => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/query/metrics', {
        params: { index: Math.floor(messageIndex/2) }
      });
      
      setSelectedMetrics(response.data);
      setMetricsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      // Optionally show an error toast or message
    }
  };

  return (
    <>
      <ScrollArea className="h-[65vh] px-4 py-2 rounded-md">
        <div className="space-y-2">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              } animate-fade-in`}
              onClick={message.sender === 'bot' 
                ? () => handleBotMessageClick(index) 
                : undefined}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground cursor-pointer hover:border hover:border-black transition-colors'
                }`}
              >
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    ul: ({node, ...props}) => (
                      <ul className="list-disc list-inside pl-2 space-y-1" {...props} />
                    ),
                    ol: ({node, ...props}) => (
                      <ol className="list-decimal list-inside pl-2 space-y-1" {...props} />
                    ),
                    li: ({node, ...props}) => (
                      <li className="text-sm leading-relaxed" {...props} />
                    ),
                    strong: ({node, ...props}) => (
                      <strong className="font-semibold" {...props} />
                    ),
                    h1: ({node, ...props}) => (
                      <h1 className="text-lg font-semibold mb-1" {...props} />
                    ),
                    h2: ({node, ...props}) => (
                      <h2 className="text-base font-semibold mb-1" {...props} />
                    ),
                    p: ({node, ...props}) => (
                      <p className="text-sm leading-relaxed" {...props} />
                    ),
                    code: ({node, ...props}) => (
                      <code className={`px-1 py-0.5 rounded text-sm ${
                        message.sender === 'user' 
                          ? 'bg-primary/20 text-primary-foreground'
                          : 'bg-secondary/50 text-secondary-foreground'
                      }`} {...props} />
                    ),
                  }}
                  className="prose dark:prose-invert max-w-none"
                >
                  {message.text}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={scrollRef} />
        </div>
        <style jsx global>{`
          .animate-fade-in {
            animation: fadeIn 0.3s ease-out;
          }
          
          @keyframes fadeIn {
            from {
              opacity: 0;
            }
            to {
              opacity: 1;
            }
          }
        `}</style>
      </ScrollArea>

      {/* Metrics Dialog */}
      <MetricsDialog 
        isOpen={metricsDialogOpen}
        onOpenChange={setMetricsDialogOpen}
        metrics={selectedMetrics}
      />
    </>
  )
}