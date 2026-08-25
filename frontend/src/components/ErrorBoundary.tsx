import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-4xl mx-auto space-y-4 bg-white rounded shadow text-red-600">
          <h1 className="text-xl font-bold">Something went wrong.</h1>
          <p className="font-semibold">{this.state.error?.toString()}</p>
          <pre className="whitespace-pre-wrap text-sm bg-red-50 p-4 rounded overflow-auto border border-red-200">
            {this.state.errorInfo?.componentStack}
          </pre>
          <pre className="whitespace-pre-wrap text-sm bg-red-50 p-4 rounded overflow-auto border border-red-200 mt-4">
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
