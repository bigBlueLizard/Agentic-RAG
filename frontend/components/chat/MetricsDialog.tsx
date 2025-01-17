import React from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription 
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from "@/components/ui/accordion";
import { 
  FileText, 
  Link, 
  Clock, 
  CreditCard, 
  Server 
} from "lucide-react";

interface MetricsDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  metrics: any;
}

export function MetricsDialog({ isOpen, onOpenChange, metrics }: MetricsDialogProps) {
  // Safely extract metrics
  const tokenUsage = metrics?.token_usage || 0;
  const cost = metrics?.cost || 0;
  const latency = metrics?.latency || 0;
  const retrievedEndpoints = metrics?.retrieved_endpoints || [];
  const agentOutputs = metrics?.agent_outputs || {};

  // Find the response generator output
  const responseGeneratorOutput = agentOutputs['response generator'] 

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Query Metrics</DialogTitle>
          <DialogDescription>Detailed breakdown of the query processing</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4">
          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="mr-2 h-5 w-5" /> Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Token Usage:</span>
                  <Badge variant="secondary">{tokenUsage}</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Cost:</span>
                  <Badge variant="secondary">${cost.toFixed(6)}</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Latency:</span>
                  <Badge variant="secondary">{latency.toFixed(2)}s</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Response Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="mr-2 h-5 w-5" /> Response Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm">{responseGeneratorOutput}</pre>
            </CardContent>
          </Card>

          {/* Retrieved Endpoints */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Link className="mr-2 h-5 w-5" /> Retrieved Endpoints
              </CardTitle>
            </CardHeader>
            <CardContent>
              {retrievedEndpoints.map((endpoint, index) => (
                <div key={index} className="mb-2">
                  <Badge variant="outline">{endpoint}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Agent Outputs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Server className="mr-2 h-5 w-5" /> Agent Outputs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible>
                {Object.entries(agentOutputs).map(([agent, outputs], index) => (
                  <AccordionItem value={`item-${index}`} key={agent}>
                    <AccordionTrigger>{agent}</AccordionTrigger>
                    <AccordionContent>
                      {outputs.map((output, idx) => (
                        <pre key={idx} className="text-xs overflow-x-auto bg-secondary/20 p-2 rounded mt-1">
                          {output[0]}
                        </pre>
                      ))}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}