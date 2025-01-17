import React from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function LLMSelector({ selectedLLM = 'gemini', onLLMChange }: { 
  selectedLLM?: string, 
  onLLMChange?: (llm: string) => void 
}) {
  return (
    <Select value={selectedLLM} onValueChange={onLLMChange}>
      <SelectTrigger className="">
        <SelectValue placeholder="Choose LLM" />
      </SelectTrigger>
      <SelectContent>
        {['gemma agents', 'gemini agents', 'gemini pro agents', 'llama 9b agents'].map((llm) => (
          <SelectItem key={llm} value={llm} className="text-xs">{llm}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}