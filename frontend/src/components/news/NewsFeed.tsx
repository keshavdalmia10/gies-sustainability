import { useEffect, useState } from 'react'
import { ExternalLink, Lightbulb, Loader2, Newspaper } from 'lucide-react'
import './NewsFeed.css'

interface NewsArticle {
  title: string
  description: string
  url: string
  source: string
  published_at: string
  image_url: string | null
  ai_insight: string | null
}

export default function NewsFeed() {
  const [articles, setArticles] = useState<NewsArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('/api/v1/news/sdg')
        if (!response.ok) {
          throw new Error('Failed to fetch news')
        }
        const data = await response.json()
        setArticles(data.articles)
      } catch (err) {
        console.error(err)
        setError('Unable to load latest news. Please try again later.')
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [])

  if (loading) {
    return (
      <div className="news-loading card">
        <Loader2 size={28} className="news-spin" />
        <p className="mb-0">Loading current SDG headlines...</p>
      </div>
    )
  }

  if (error) {
    return <div className="news-error card">{error}</div>
  }

  if (articles.length === 0) {
    return (
      <div className="news-empty card">
        <p className="mb-0">No articles available right now. Check back after the next sync cycle.</p>
      </div>
    )
  }

  return (
    <div className="news-feed">
      <header className="news-feed-head">
        <div className="news-feed-icon" aria-hidden="true">
          <Newspaper size={20} />
        </div>
        <div>
          <h3 className="mb-0">Global SDG News</h3>
          <p className="mb-0">Curated updates with AI-highlighted research opportunities.</p>
        </div>
      </header>

      <div className="news-grid">
        {articles.map((article, index) => (
          <article key={`${article.title}-${index}`} className="news-card card">
            {article.image_url ? (
              <div className="news-image-wrap">
                <img
                  src={article.image_url}
                  alt={article.title}
                  onError={(event) => {
                    ;(event.target as HTMLImageElement).style.display = 'none'
                  }}
                />
                <span className="news-source-badge">{article.source}</span>
              </div>
            ) : (
              <div className="news-image-fallback">
                <span className="news-source-badge">{article.source}</span>
              </div>
            )}

            <div className="news-content">
              <p className="news-date mb-0">
                {article.published_at
                  ? new Date(article.published_at).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  : 'Just now'}
              </p>

              <h4>
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  {article.title}
                </a>
              </h4>

              <p className="news-description">{article.description}</p>

              {article.ai_insight && (
                <div className="news-insight">
                  <div className="news-insight-head">
                    <Lightbulb size={14} />
                    <span>AI Suggestion</span>
                  </div>
                  <p className="mb-0">{article.ai_insight.replace('Research Opportunity:', '').trim()}</p>
                </div>
              )}

              <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">
                Read Full Story <ExternalLink size={14} />
              </a>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
