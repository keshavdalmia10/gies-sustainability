import React, { useEffect, useState } from 'react';
import { ExternalLink, Lightbulb, Loader2, Newspaper } from 'lucide-react';

interface NewsArticle {
  title: string;
  description: string;
  url: string;
  source: string;
  published_at: string;
  image_url: string | null;
  ai_insight: string | null;
}

const NewsFeed: React.FC = () => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('/api/v1/news/sdg');
        if (!response.ok) {
          throw new Error('Failed to fetch news');
        }
        const data = await response.json();
        setArticles(data.articles);
      } catch (err) {
        console.error(err);
        setError('Unable to load latest news. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg shadow-indigo-200">
            <Newspaper className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Global SDG News</h2>
            <p className="text-base text-gray-500 font-medium">Curated updates & AI-powered research opportunities</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {articles.map((article, index) => (
          <div key={index} className="group relative bg-white rounded-[2rem] shadow-sm border border-gray-100 hover:shadow-2xl hover:shadow-indigo-100/50 transition-all duration-500 flex flex-col h-full overflow-hidden hover:-translate-y-2">
            
            {/* Image Section */}
            {article.image_url && (
              <div className="h-64 overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent z-10 opacity-90" />
                <img 
                  src={article.image_url} 
                  alt={article.title} 
                  className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700 ease-out"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&auto=format&fit=crop&q=60';
                  }}
                />
                
                {/* Floating Source Badge */}
                <div className="absolute top-4 left-4 z-20">
                  <span className="px-3 py-1.5 bg-white/95 backdrop-blur-md text-xs font-bold text-indigo-900 rounded-full shadow-lg border border-white/50">
                    {article.source}
                  </span>
                </div>

                {/* Date Badge */}
                <div className="absolute bottom-4 left-4 z-20">
                  <span className="text-white/90 text-xs font-medium bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm border border-white/10">
                    {article.published_at ? new Date(article.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Just Now'}
                  </span>
                </div>
              </div>
            )}
            
            <div className="p-7 flex-1 flex flex-col relative">
              {/* Decorative background blob */}
              <div className="absolute top-0 right-0 -mt-10 -mr-10 w-32 h-32 bg-indigo-50 rounded-full blur-3xl opacity-50 pointer-events-none"></div>

              <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 leading-tight group-hover:text-indigo-600 transition-colors relative z-10">
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  {article.title}
                </a>
              </h3>
              
              <p className="text-sm text-gray-600 mb-6 line-clamp-3 leading-relaxed relative z-10">
                {article.description}
              </p>
              
              {/* AI Insight Box - The "Colour Box" */}
              {article.ai_insight && (
                <div className="mt-auto relative group/ai">
                  <div className="absolute inset-0 bg-gradient-to-r from-violet-100 to-fuchsia-100 rounded-2xl transform rotate-1 group-hover/ai:rotate-2 transition-transform duration-300"></div>
                  <div className="relative bg-white/60 backdrop-blur-sm border border-violet-100 rounded-2xl p-5 hover:bg-white/80 transition-colors">
                    <div className="flex items-center space-x-2.5 mb-3">
                      <div className="p-1.5 bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-lg shadow-sm">
                        <Lightbulb className="w-3.5 h-3.5 text-white" />
                      </div>
                      <span className="text-xs font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-fuchsia-600 uppercase tracking-wider">
                        AI Suggestion
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 font-medium leading-relaxed">
                      {article.ai_insight.replace("Research Opportunity:", "").trim()}
                    </p>
                  </div>
                </div>
              )}
              
              <div className="mt-6 pt-2 flex justify-end">
                <a 
                  href={article.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-sm font-bold text-gray-900 hover:text-indigo-600 transition-colors group/link"
                >
                  Read Full Story
                  <ExternalLink className="w-4 h-4 ml-2 transform group-hover/link:translate-x-1 group-hover/link:-translate-y-1 transition-transform duration-300 text-gray-400 group-hover/link:text-indigo-600" />
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NewsFeed;
