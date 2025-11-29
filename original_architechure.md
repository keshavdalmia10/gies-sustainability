# Gies Sustainability Dashboard

## Introduction and Purpose
The Gies Sustainability Dashboard is an intelligent analytics platform designed to track and visualize sustainability research contributions from faculty at the Gies College of Business, University of Illinois. The dashboard automatically identifies research publications that contribute to the United Nations' 17 Sustainable Development Goals (SDGs) and provides comprehensive insights into the college's sustainability impact.

### Key Objectives:
*   Measure faculty contributions to global sustainability goals
*   Identify research trends and emerging sustainability themes
*   Support strategic decision-making for sustainability initiatives
*   Showcase Gies College's commitment to sustainable business practices

## Data Collection and Sources

### Faculty Profile Collection
The system automatically gathers faculty information through two primary methods:
*   **Illinois Experts API Integration**:
    *   Connects directly to the university's research database
    *   Retrieves faculty profiles, affiliations, and basic research information
    *   Maintains active status tracking for current faculty members
*   **Web-Based Data Enhancement**:
    *   Uses automated web scraping to supplement faculty information
    *   Collects additional research metadata and publication details
    *   Employs sophisticated rate-limiting and anti-detection measures to ensure reliable data collection

### Journal Database Integration
*   Cross-references publications with prestigious journal rankings
*   Identifies publications in top-tier business journals (Financial Times, UT Dallas lists)
*   Categorizes journals by business domain and academic impact

### Keyword and Research Theme Extraction
*   Automatically extracts research keywords from faculty profiles
*   Maps research themes to sustainability domains
*   Maintains comprehensive keyword rankings and associations

## Sustainability Classification System

### Two-Stage AI-Powered Analysis
The system employs a sophisticated artificial intelligence approach to determine sustainability relevance:

#### Stage 1: Sustainability Relevance Detection
*   Uses advanced language models to analyze research titles and abstracts
*   Applies detailed SDG definitions to determine if research contributes to any of the 17 sustainability goals
*   Binary classification: determines whether research is sustainability-related or not
*   Considers both direct applications and foundational research that supports sustainability goals

#### Stage 2: Specific SDG Goal Identification
*   For sustainability-relevant research, identifies the most applicable SDG goals
*   Uses vector similarity search with FAISS technology to match research content with detailed SDG descriptions
*   Ranks the top 3 most relevant SDG goals for each publication
*   Provides weighted relevance scores for nuanced analysis

### SDG Classification Framework
The system evaluates research against all 17 UN Sustainable Development Goals:
1.  **No Poverty** - Economic inclusion and poverty eradication research
2.  **Zero Hunger** - Food security and sustainable agriculture studies
3.  **Good Health and Well-Being** - Healthcare access and medical advancement research
4.  **Quality Education** - Educational equity and learning opportunity studies
5.  **Gender Equality** - Gender empowerment and equality research
6.  **Clean Water and Sanitation** - Water resource and sanitation management studies
7.  **Affordable and Clean Energy** - Renewable energy and energy access research
8.  **Decent Work and Economic Growth** - Sustainable economic development studies
9.  **Industry, Innovation, and Infrastructure** - Sustainable industrialization research
10. **Reduced Inequality** - Social and economic inequality reduction studies
11. **Sustainable Cities and Communities** - Urban sustainability and community development
12. **Responsible Consumption and Production** - Circular economy and sustainable consumption research
13. **Climate Action** - Climate change mitigation and adaptation studies
14. **Life Below Water** - Marine conservation and ocean sustainability research
15. **Life on Land** - Terrestrial ecosystem and biodiversity studies
16. **Peace, Justice, and Strong Institutions** - Governance and institutional development research
17. **Partnerships for the Goals** - Collaborative approaches to sustainability

## Data Architecture and Management

### Core Data Structure

#### Faculty Records
*   Personal identifiers, department affiliations, and contact information
*   Active status tracking and historical employment data
*   Research keyword profiles and expertise areas

#### Publication Database
*   Comprehensive article metadata (titles, abstracts, publication years)
*   DOI linking and citation information
*   Journal classifications and impact ratings
*   Sustainability scores and SDG mappings

#### Sustainability Analytics
*   Binary sustainability flags and confidence scores
*   Ranked SDG relevance assignments (top 3 per publication)
*   Temporal trends and growth rate calculations
*   Department and faculty-level aggregations
2● Maps research themes to sustainability domains● Maintains comprehensive keyword rankings and associationsSustainability Classification SystemTwo-Stage AI-Powered AnalysisThe system employs a sophisticated artificial intelligence approach to determine sustainabilityrelevance:Stage 1: Sustainability Relevance Detection● Uses advanced language models to analyze research titles and abstracts● Applies detailed SDG definitions to determine if research contributes to any of the 17sustainability goals● Binary classification: determines whether research is sustainability-related or not● Considers both direct applications and foundational research that supports sustainabilitygoalsStage 2: Specific SDG Goal Identification● For sustainability-relevant research, identifies the most applicable SDG goals● Uses vector similarity search with FAISS technology to match research content withdetailed SDG descriptions● Ranks the top 3 most relevant SDG goals for each publication● Provides weighted relevance scores for nuanced analysisSDG Classification FrameworkThe system evaluates research against all 17 UN Sustainable Development Goals:1. No Poverty - Economic inclusion and poverty eradication research2. Zero Hunger - Food security and sustainable agriculture studies3. Good Health and Well-Being - Healthcare access and medical advancement research4. Quality Education - Educational equity and learning opportunity studies5. Gender Equality - Gender empowerment and equality research6. Clean Water and Sanitation - Water resource and sanitation management studies7. Affordable and Clean Energy - Renewable energy and energy access research8. Decent Work and Economic Growth - Sustainable economic development studies9. Industry, Innovation, and Infrastructure - Sustainable industrialization research10. Reduced Inequality - Social and economic inequality reduction studies11. Sustainable Cities and Communities - Urban sustainability and communitydevelopment12. Responsible Consumption and Production - Circular economy and sustainableconsumption research13. Climate Action - Climate change mitigation and adaptation studies
314. Life Below Water - Marine conservation and ocean sustainability research15. Life on Land - Terrestrial ecosystem and biodiversity studies16. Peace, Justice, and Strong Institutions - Governance and institutional developmentresearch17. Partnerships for the Goals - Collaborative approaches to sustainabilityData Architecture and ManagementCore Data StructureFaculty Records● Personal identifiers, department affiliations, and contact information● Active status tracking and historical employment data● Research keyword profiles and expertise areasPublication Database● Comprehensive article metadata (titles, abstracts, publication years)● DOI linking and citation information● Journal classifications and impact ratings● Sustainability scores and SDG mappingsSustainability Analytics● Binary sustainability flags and confidence scores● Ranked SDG relevance assignments (top 3 per publication)● Temporal trends and growth rate calculations● Department and faculty-level aggregationsDashboard Features and CapabilitiesAnalytics and Visualization● Department-level Analysis: Compare sustainability contributions across academicdepartments● Faculty Performance Metrics: Individual and comparative faculty sustainability impact● Publication Trend Analysis: Temporal patterns and growth rates in sustainabilityresearch● SDG Goal Distribution: Visual representation of research alignment with specificsustainability goalsInteractive Search and Discovery● Semantic Search: AI-powered search that understands research concepts and themes
4● Advanced Filtering: Filter by department, publication year, SDG goals, and journaltypes● Research Similarity: Discover related research through content-basedrecommendationsImpact Metrics and Reporting● Sustainability Ratios: Percentage of research contributing to sustainability goals● Faculty Engagement: Number of faculty actively contributing to sustainability research● Growth Indicators: Year-over-year trends and momentum metrics● Journal Impact Analysis: Quality and reach of sustainability publicationsTechnical Architecture OverviewFrontend Dashboard● Built with modern React technology for responsive, interactive user experience● Real-time data visualization with dynamic charts and graphs● Mobile-friendly design for accessibility across devicesBackend Processing Pipeline● Python-based data processing for robust academic data handling● Automated scheduling for regular data updates and maintenance● API integration for seamless data flow between systemsAI and Machine Learning Services● OpenAI GPT models for sophisticated text analysis and classification● FAISS vector database for high-performance similarity search● Pinecone cloud platform for scalable vector operationsSystem Benefits and ImpactFor Academic Leadership:● Evidence-based insights for strategic sustainability planning● Clear metrics for reporting sustainability research impact● Identification of emerging research strengths and opportunitiesFor Faculty:● Recognition of sustainability research contributions● Discovery of collaboration opportunities with like-minded researchers● Understanding of research alignment with global sustainability goals
5For Institutional Reporting:● Comprehensive data for sustainability rankings and accreditation● Quantifiable metrics for grant applications and funding requests● Transparent documentation of sustainability research impactThis dashboard represents a significant advancement in academic sustainability tracking,combining cutting-edge AI technology with comprehensive data collection to provideunprecedented insights into research impact on global sustainability challenges.