import React from 'react'

type Props = {
  children: React.ReactNode
}

type State = {
  hasError: boolean
}

export default class RouteErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Route render error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="container page-shell">
          <div className="card">
            <h2 className="card-title">This view failed to render</h2>
            <p className="mb-0">
              Try refreshing the page. If the problem persists, check backend API responses and browser console logs.
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
