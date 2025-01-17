'use client'
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, AlertCircle, CheckCircle2, Edit, FileText, Trash2, Shield } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export default function OpenAPIEditor() {
  const [uploadStatus, setUploadStatus] = useState({ type: '', message: '' });
  const [selectedFile, setSelectedFile] = useState(null);
  const [routes, setRoutes] = useState({
    get: [],
    post: [],
    put: [],
    delete: []
  });
  const [apiSpec, setApiSpec] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [approvalStatus, setApprovalStatus] = useState({});

  // Fetch OpenAPI JSON when component mounts
  useEffect(() => {
    const fetchOpenAPISpec = async () => {
      try {
        const response = await fetch('http://localhost:5000/api_docs');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonContent = await response.json();

        // Debug logging
        console.log('Received API specification:', jsonContent);
        console.log('Paths:', jsonContent.paths);

        processApiSpec(jsonContent);
      } catch (error) {
        console.error('Error fetching API specification:', error);
        setUploadStatus({
          type: 'error',
          message: 'Failed to load API specification. ' + error.message
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchOpenAPISpec();
  }, []); // Empty dependency array means this runs once on mount

  const processApiSpec = (jsonContent) => {
    setApiSpec(jsonContent);

    // Organize routes by method
    const newRoutes = {
      get: [],
      post: [],
      put: [],
      delete: []
    };

    // Enhanced logging and error checking
    if (!jsonContent.paths) {
      console.error('No paths found in API specification');
      setUploadStatus({
        type: 'error',
        message: 'Invalid API specification: No paths found'
      });
      return;
    }

    try {
      Object.entries(jsonContent.paths).forEach(([path, methods]) => {
        Object.entries(methods).forEach(([method, details]) => {
          // Convert method to lowercase to match our routes object keys
          const normalizedMethod = method.toLowerCase();

          if (newRoutes[normalizedMethod]) {
            newRoutes[normalizedMethod].push({
              path,
              ...details
            });
          } else {
            console.warn(`Unhandled HTTP method: ${method}`);
          }
        });
      });

      // Debug logging of processed routes
      console.log('Processed Routes:', newRoutes);

      setRoutes(newRoutes);
      setUploadStatus({
        type: 'success',
        message: 'API specification successfully loaded'
      });
    } catch (error) {
      console.error('Error processing API specification:', error);
      setUploadStatus({
        type: 'error',
        message: 'Failed to process API specification: ' + error.message
      });
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.name.endsWith('.json')) {
        setUploadStatus({
          type: 'error',
          message: 'Please select a JSON file'
        });
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setUploadStatus({ type: '', message: '' });
    }
  };

  const handleConfirmUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        setIsLoading(true);
        const response = await fetch('http://localhost:5000/upload/upload_openapi', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('File upload failed');
        }

        // Fetch the updated API specification after upload
        const apiDocResponse = await fetch('http://localhost:5000/api_docs');

        if (!apiDocResponse.ok) {
          throw new Error('Failed to fetch updated API specification');
        }

        const jsonContent = await apiDocResponse.json();

        processApiSpec(jsonContent);

        setSelectedFile(null);
      } catch (error) {
        console.error('Upload error:', error);
        setUploadStatus({
          type: 'error',
          message: 'Error uploading file: ' + error.message
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const methodColors = {
    get: 'border-blue-200',
    post: 'border-green-200',
    put: 'border-yellow-200',
    delete: 'border-red-200'
  };

  const RouteActions = ({ method, path }) => {
    const toggleApproval = () => {
      setApprovalStatus(prev => ({
        ...prev,
        [`${method}_${path}`]: !prev[`${method}_${path}`]
      }));
    };

    return (
      <div className="flex gap-2 text-xs">
        <button className="flex items-center gap-1 text-blue-600 hover:text-blue-800">
          <Edit className="w-3 h-3" />
          Edit
        </button>
        <button className="flex items-center gap-1 text-gray-600 hover:text-gray-800">
          <FileText className="w-3 h-3" />
          Docs
        </button>
        <button className="flex items-center gap-1 text-red-600 hover:text-red-800">
          <Trash2 className="w-3 h-3" />
          Delete
        </button>
        <button 
          onClick={toggleApproval}
          className={`flex items-center gap-1 ${
            approvalStatus[`${method}_${path}`] 
              ? 'text-green-600 hover:text-green-800' 
              : 'text-yellow-600 hover:text-yellow-800'
          }`}
        >
          <Shield className="w-3 h-3" />
          {approvalStatus[`${method}_${path}`] ? 'Approval Required' : 'Approval Not Required'}
        </button>
      </div>
    );
  };

  const SchemaView = ({ schema, title }) => {
    if (!schema) return null;

    return (
      <div className="flex-1">
        <h4 className="text-sm font-medium mb-2">{title}</h4>
        <div className="bg-gray-200 p-3 rounded-md">
          <pre className="text-xs overflow-auto">
            {JSON.stringify(schema, null, 2)}
          </pre>
        </div>
      </div>
    );
  };

  const RouteDetails = ({ route, method }) => (
    <div className="space-y-4">
      {route.description && (
        <div className="text-sm text-gray-600 border-l-2 border-gray-300 pl-3">
          {route.description}
        </div>
      )}
      <div className="flex gap-4">
        <SchemaView
          schema={{
            parameters: route.parameters,
            requestBody: route.requestBody?.content?.['application/json']?.schema
          }}
          title="Request Schema"
        />
        <SchemaView
          schema={route.responses?.['200']?.content?.['application/json']?.schema}
          title="Response Schema"
        />
      </div>
    </div>
  );

  return (
    <Card className="w-full mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Documentation Editor</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg border-gray-300 hover:bg-gray-100 transition-colors">
          <label htmlFor="file-upload" className="w-full">
            <input
              id="file-upload"
              type="file"
              accept=".json"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Button
              variant="outline"
              className="w-full flex items-center justify-center gap-2"
              asChild
            >
              <span>
                <Upload className="w-4 h-4" />
                Select JSON File
              </span>
            </Button>
          </label>
          <span className="flex mt-2">We accept <pre> openapi.json </pre> files for ingesting the documentation.</span>
          {selectedFile && (
            <div className="mt-4 w-full space-y-2">
              <p className="text-sm text-gray-600 text-center">
                Selected: {selectedFile.name}
              </p>
              <Button
                className="w-full"
                onClick={handleConfirmUpload}
                disabled={isLoading}
              >
                {isLoading ? 'Uploading...' : 'Confirm Upload'}
              </Button>
            </div>
          )}
        </div>

        {!isLoading && uploadStatus.type === 'success' && (
          <div className="space-y-4">
            {Object.entries(routes).map(([method, paths]) =>
              paths.length > 0 && (
                <Accordion key={method} type="single" collapsible className="w-full">
                  <AccordionItem value="method" className={`${methodColors[method]} border rounded-lg`}>
                    <AccordionTrigger className="px-4">
                      {method.toUpperCase()} Routes ({paths.length})
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-2">
                        {paths.map((route, index) => (
                          <Accordion key={index} type="single" collapsible className="w-full">
                            <AccordionItem value="route" className="border rounded">
                              <AccordionTrigger className="px-4 py-2">
                                <div className="flex justify-between items-center w-full">
                                  <span className="font-mono text-sm">{route.path}</span>
                                  <RouteActions method={method} path={route.path} />
                                </div>
                              </AccordionTrigger>
                              <AccordionContent className="px-4 py-4">
                                <RouteDetails route={route} method={method} />
                              </AccordionContent>
                            </AccordionItem>
                          </Accordion>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}