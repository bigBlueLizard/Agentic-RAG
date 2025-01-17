import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from "@/components/ui/dialog"
  import { Button } from "@/components/ui/button"
  
  interface APIDetails {
    endpoints: string[];
    documentation_details: Array<{
      parameters: any;
      body: any;
      url: string;
      method: string;
    }>;
    responses: any[];
  }
  
  interface APIDetailsModalProps {
    documents?: {
      endpoints: string[];
      documentation_details: Array<{
        parameters: any;
        body: any;
        url: string;
        method: string;
      }>;
      responses: any[];
    };
  }
  
  export function APIDetailsModal({ documents }: APIDetailsModalProps) {
    if (!documents) return null;
  
    return (
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="link" className="text-xs text-blue-500 hover:text-blue-700">
            View API Details
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>API Request Details</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Endpoints:</h3>
              <ul className="list-disc pl-5 space-y-1">
                {documents.endpoints.map((endpoint, index) => (
                  <li key={index} className="text-sm">{endpoint}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Documentation:</h3>
              {documents.documentation_details.map((doc, index) => (
                <div key={index} className="mb-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium">Endpoint {index + 1}:</p>
                  <div className="mt-2 space-y-2">
                    <p className="text-sm"><span className="font-medium">URL:</span> {doc.url}</p>
                    <p className="text-sm"><span className="font-medium">Method:</span> {doc.method}</p>
                    <div>
                      <p className="text-sm font-medium">Parameters:</p>
                      <pre className="text-xs bg-gray-100 p-2 rounded mt-1">
                        {JSON.stringify(doc.parameters, null, 2)}
                      </pre>
                    </div>
                    {Object.keys(doc.body).length > 0 && (
                      <div>
                        <p className="text-sm font-medium">Body:</p>
                        <pre className="text-xs bg-gray-100 p-2 rounded mt-1">
                          {JSON.stringify(doc.body, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Responses:</h3>
              <div className="space-y-2">
                {documents.responses.map((response, index) => (
                  <div key={index}>
                    <p className="text-sm font-medium">Response {index + 1}:</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }