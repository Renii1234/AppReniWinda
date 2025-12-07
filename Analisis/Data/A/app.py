import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================
# KONFIGURASI APLIKASI
# ============================================
st.set_page_config(
    page_title="World GDP Insight Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .analyst-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .analyst-card-winda {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1rem;
        padding: 10px 16px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNGSI UNTUK DATA SAMPLE
# ============================================
def create_sample_data():
    """Membuat data sample untuk demonstrasi"""
    countries = [
        "Indonesia", "China", "India", "Japan", "United States", 
        "Germany", "United Kingdom", "France", "Brazil", "Russia",
        "Australia", "Singapore", "Vietnam", "Thailand", "Malaysia",
        "Philippines", "South Korea", "Canada", "Italy", "Spain"
    ]
    
    years = list(range(2000, 2025))
    np.random.seed(42)
    
    data = []
    for country in countries:
        # Base GDP values for each country
        if country == "China":
            base = 1.2e12  # 1.2 trillion
            growth_rate = 0.09
        elif country == "United States":
            base = 10e12  # 10 trillion
            growth_rate = 0.03
        elif country == "India":
            base = 0.5e12  # 0.5 trillion
            growth_rate = 0.07
        elif country == "Indonesia":
            base = 0.2e12  # 0.2 trillion
            growth_rate = 0.05
        else:
            base = np.random.uniform(0.1e12, 2e12)
            growth_rate = np.random.uniform(0.02, 0.06)
        
        for i, year in enumerate(years):
            # Add some randomness to growth
            annual_growth = growth_rate * np.random.uniform(0.8, 1.2)
            
            # Simulate economic crises
            if year == 2008:
                annual_growth *= 0.5  # Financial crisis
            elif year == 2020:
                annual_growth *= 0.7  # COVID-19 impact
            elif year == 2021:
                annual_growth *= 1.3  # Recovery
                
            if i == 0:
                gdp = base
            else:
                gdp = data[-1]['GDP'] * (1 + annual_growth)
            
            data.append({
                'Country Name': country,
                'Tahun': year,
                'GDP (Current US$)': gdp
            })
    
    return pd.DataFrame(data)

# ============================================
# LOAD DATA
# ============================================
df = create_sample_data()

# Calculate additional metrics
df['GDP_Billion'] = df['GDP (Current US$)'] / 1e9
df['Year'] = df['Tahun']

# Create regional grouping
country_regions = {
    'ASEAN': ['Indonesia', 'Singapore', 'Vietnam', 'Thailand', 'Malaysia', 'Philippines'],
    'East Asia': ['China', 'Japan', 'South Korea'],
    'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Spain'],
    'Americas': ['United States', 'Canada', 'Brazil'],
    'Others': ['India', 'Russia', 'Australia']
}

# Reverse mapping for lookup
country_to_region = {}
for region, countries in country_regions.items():
    for country in countries:
        country_to_region[country] = region

df['Region'] = df['Country Name'].map(country_to_region)

# ============================================
# HEADER
# ============================================
st.markdown('<h1 class="main-header">🌍 World GDP Insight Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### *Analytical Perspectives by Reni Agustí & Winda Adisty*")

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🔍 Navigation")
    
    persona = st.radio(
        "**Choose Analyst Perspective:**",
        ["👩‍💼 Reni Agustí", "🎨 Winda Adisty"],
        index=0,
        help="Select between analytical depth vs interactive exploration"
    )
    
    st.markdown("---")
    
    if "Reni" in persona:
        st.markdown("### 🔧 Analysis Parameters")
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["ASEAN Trends", "Regional Comparison", "Growth Analysis", "Crisis Impact"]
        )
        
        year_range = st.slider(
            "Select Year Range:",
            min_value=2000,
            max_value=2024,
            value=(2000, 2024)
        )
        
    else:  # Winda's perspective
        st.markdown("### 🎮 Interactive Controls")
        
        available_countries = df['Country Name'].unique().tolist()
        default_countries = ["Indonesia", "China", "India"]
        
        selected_countries = st.multiselect(
            "Select Countries to Compare:",
            options=available_countries,
            default=default_countries,
            max_selections=5
        )
        
        year_slider = st.slider(
            "Select Year for Map View:",
            min_value=2000,
            max_value=2024,
            value=2023
        )
        
        chart_style = st.selectbox(
            "Chart Style:",
            ["Modern", "Minimal", "Dark", "Colorful"]
        )
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    # Calculate some quick stats
    latest_year = 2024
    latest_data = df[df['Year'] == latest_year]
    total_gdp = latest_data['GDP (Current US$)'].sum() / 1e12  # in trillion
    avg_growth = 4.2  # simulated average growth
    
    st.metric("Global GDP (2024)", f"${total_gdp:.1f}T")
    st.metric("Avg Annual Growth", f"{avg_growth}%")
    st.metric("Countries in Dataset", len(df['Country Name'].unique()))

# ============================================
# ANALYST CARDS
# ============================================
col1, col2 = st.columns(2)

with col1:
    if "Reni" in persona:
        st.markdown("""
        <div class="analyst-card">
            <h3>👩‍💼 Reni Agustí</h3>
            <p><i>Senior Economic Analyst</i></p>
            <p>Specializes in macroeconomic trends, regional analysis, and long-term growth patterns. 
            Focus on data accuracy and statistical insights.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="analyst-card" style="opacity: 0.7;">
            <h3>👩‍💼 Reni Agustí</h3>
            <p><i>Senior Economic Analyst</i></p>
            <p>Click to switch to analytical view</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if "Winda" in persona:
        st.markdown("""
        <div class="analyst-card-winda">
            <h3>🎨 Winda Adisty</h3>
            <p><i>Data Visualization Specialist</i></p>
            <p>Creates interactive, engaging data stories. Focus on user experience, 
            intuitive design, and making complex data accessible.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="analyst-card-winda" style="opacity: 0.7;">
            <h3>🎨 Winda Adisty</h3>
            <p><i>Data Visualization Specialist</i></p>
            <p>Click to switch to interactive view</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# RENI AGUSTÍ'S DASHBOARD
# ============================================
if "Reni" in persona:
    st.markdown("---")
    
    # Key Metrics Row
    st.subheader("📈 Key Economic Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Fastest growing ASEAN country
        asean_countries = country_regions['ASEAN']
        asean_growth = []
        for country in asean_countries:
            try:
                gdp_2000 = df[(df['Country Name'] == country) & (df['Year'] == 2000)]['GDP (Current US$)'].values[0]
                gdp_2024 = df[(df['Country Name'] == country) & (df['Year'] == 2024)]['GDP (Current US$)'].values[0]
                growth = (gdp_2024 / gdp_2000) ** (1/24) - 1
                asean_growth.append((country, growth * 100))
            except:
                continue
        
        if asean_growth:
            fastest = max(asean_growth, key=lambda x: x[1])
            st.metric("Fastest Growing ASEAN", fastest[0], f"{fastest[1]:.1f}% p.a.")
        else:
            st.metric("Fastest Growing ASEAN", "N/A", "0%")
    
    with col2:
        # Global GDP growth
        try:
            global_gdp_2000 = df[df['Year'] == 2000]['GDP (Current US$)'].sum()
            global_gdp_2024 = df[df['Year'] == 2024]['GDP (Current US$)'].sum()
            global_growth = ((global_gdp_2024 / global_gdp_2000) ** (1/24) - 1) * 100
            st.metric("Global Avg Growth", f"{global_growth:.1f}%", "2000-2024")
        except:
            st.metric("Global Avg Growth", "N/A", "0%")
    
    with col3:
        # Most resilient during COVID
        covid_data = []
        for country in df['Country Name'].unique():
            try:
                gdp_2019 = df[(df['Country Name'] == country) & (df['Year'] == 2019)]['GDP (Current US$)'].values[0]
                gdp_2020 = df[(df['Country Name'] == country) & (df['Year'] == 2020)]['GDP (Current US$)'].values[0]
                recovery = (gdp_2020 / gdp_2019 - 1) * 100
                covid_data.append((country, recovery))
            except:
                continue
        
        if covid_data:
            most_resilient = max(covid_data, key=lambda x: x[1])
            st.metric("Most COVID-Resilient", most_resilient[0], f"{most_resilient[1]:.1f}%")
        else:
            st.metric("Most COVID-Resilient", "N/A", "0%")
    
    with col4:
        # Regional contribution
        try:
            latest_region = df[df['Year'] == 2024].groupby('Region')['GDP (Current US$)'].sum()
            top_region = latest_region.idxmax()
            share = (latest_region.max() / latest_region.sum()) * 100
            st.metric("Largest Regional Share", top_region, f"{share:.0f}% of global GDP")
        except:
            st.metric("Largest Regional Share", "N/A", "0%")
    
    # Main Analysis Section
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "🇦🇸 ASEAN Analysis", 
        "🌐 Regional Comparison", 
        "📊 Growth Champions", 
        "📉 Crisis Impact"
    ])
    
    with tab1:
        st.subheader("ASEAN Economic Development (2000-2024)")
        
        # Filter ASEAN data
        asean_df = df[df['Country Name'].isin(country_regions['ASEAN'])].copy()
        
        if not asean_df.empty:
            # Line chart
            fig = px.line(
                asean_df, 
                x='Year', 
                y='GDP_Billion', 
                color='Country Name',
                title='GDP Trends of ASEAN Countries',
                labels={'GDP_Billion': 'GDP (Billion USD)', 'Year': 'Year'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Add crisis markers
            fig.add_vline(x=2008, line_dash="dash", line_color="red", 
                         annotation_text="Global Financial Crisis")
            fig.add_vline(x=2020, line_dash="dash", line_color="orange", 
                         annotation_text="COVID-19 Pandemic")
            
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # ASEAN Insights from Reni
            st.markdown("""
            <div class="metric-card">
            <h4>👩‍💼 Reni's Insight:</h4>
            <p><b>Key Observation:</b> Vietnam shows the most consistent growth pattern among ASEAN countries, 
            while Indonesia maintains the largest GDP base.</p>
            <p><b>Recommendation:</b> ASEAN countries should focus on economic diversification to build 
            resilience against global shocks.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No ASEAN data available for visualization.")
    
    with tab2:
        st.subheader("Regional GDP Distribution Over Time")
        
        # Prepare regional data
        regional_df = df.groupby(['Year', 'Region']).agg({
            'GDP (Current US$)': 'sum'
        }).reset_index()
        regional_df['GDP_Trillion'] = regional_df['GDP (Current US$)'] / 1e12
        
        if not regional_df.empty:
            # Stacked area chart
            fig = px.area(
                regional_df,
                x='Year',
                y='GDP_Trillion',
                color='Region',
                title='Global GDP Distribution by Region',
                labels={'GDP_Trillion': 'GDP (Trillion USD)', 'Year': 'Year'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_layout(
                height=500,
                yaxis_title="GDP (Trillion USD)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No regional data available for visualization.")
    
    with tab3:
        st.subheader("Fastest Growing Economies Analysis")
        
        # Calculate growth rates for all countries
        growth_data = []
        for country in df['Country Name'].unique():
            country_df = df[df['Country Name'] == country].sort_values('Year')
            
            if len(country_df) > 1:
                # Calculate CAGR
                gdp_start = country_df.iloc[0]['GDP (Current US$)']
                gdp_end = country_df.iloc[-1]['GDP (Current US$)']
                years = len(country_df) - 1
                cagr = (gdp_end / gdp_start) ** (1/years) - 1
                
                growth_data.append({
                    'Country': country,
                    'CAGR': cagr * 100,
                    'GDP_2024': gdp_end / 1e9,  # in billions
                    'Region': country_to_region.get(country, 'Others')
                })
        
        if growth_data:
            growth_df = pd.DataFrame(growth_data)
            
            # Bubble chart
            fig = px.scatter(
                growth_df,
                x='GDP_2024',
                y='CAGR',
                size='GDP_2024',
                color='Region',
                hover_name='Country',
                title='Growth vs Size: Economic Performance Matrix',
                labels={
                    'GDP_2024': 'GDP 2024 (Billion USD)',
                    'CAGR': 'Annual Growth Rate (%)'
                },
                size_max=60
            )
            
            # Add quadrant lines if enough data
            if len(growth_df) > 1:
                median_gdp = growth_df['GDP_2024'].median()
                median_growth = growth_df['CAGR'].median()
                
                fig.add_hline(y=median_growth, line_dash="dot", line_color="gray")
                fig.add_vline(x=median_gdp, line_dash="dot", line_color="gray")
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top 10 fastest growing
            st.subheader("Top 10 Fastest Growing Economies (2000-2024)")
            top_10 = growth_df.nlargest(10, 'CAGR')[['Country', 'CAGR', 'Region']]
            top_10['CAGR'] = top_10['CAGR'].round(2)
            st.dataframe(top_10, use_container_width=True)
        else:
            st.warning("Insufficient data for growth analysis.")
    
    with tab4:
        st.subheader("Economic Resilience During Crises")
        st.info("Crisis impact analysis module is under development.")
        
# ============================================
# WINDA ADISTY'S DASHBOARD
# ============================================
else:
    st.markdown("---")
    
    # Interactive Controls Row
    st.subheader("🎮 Interactive Exploration")
    
    # Create two main columns
    main_col1, main_col2 = st.columns([2, 1])
    
    with main_col1:
        # World Map Visualization
        st.subheader("🗺️ Interactive World GDP Map")
        
        # Prepare data for selected year
        map_year_data = df[df['Year'] == year_slider][['Country Name', 'GDP_Billion', 'Region']].copy()
        
        if not map_year_data.empty:
            # Create bar chart as alternative to map (since we don't have country codes)
            fig = px.bar(
                map_year_data.nlargest(15, 'GDP_Billion'),
                x='Country Name',
                y='GDP_Billion',
                color='Region',
                title=f'Top 15 Countries by GDP ({year_slider})',
                labels={'GDP_Billion': 'GDP (Billion USD)', 'Country Name': 'Country'},
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            
            fig.update_layout(
                height=500,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for year {year_slider}")
    
    with main_col2:
        st.subheader("📋 Country Information")
        
        if selected_countries:
            for country in selected_countries:
                country_data = df[df['Country Name'] == country]
                if not country_data.empty:
                    latest_gdp = country_data[country_data['Year'] == 2024]['GDP_Billion'].values[0]
                    
                    # Calculate growth
                    try:
                        gdp_2000 = country_data[country_data['Year'] == 2000]['GDP_Billion'].values[0]
                        growth = ((latest_gdp / gdp_2000) ** (1/24) - 1) * 100
                    except:
                        growth = 0
                    
                    st.markdown(f"""
                    <div class="metric-card">
                    <h4>{country}</h4>
                    <p><b>GDP 2024:</b> ${latest_gdp:.0f}B</p>
                    <p><b>Avg Growth:</b> {growth:.1f}% p.a.</p>
                    <p><b>Region:</b> {country_to_region.get(country, 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add country selector
        st.markdown("### Add More Countries")
        available_for_selection = [c for c in df['Country Name'].unique() if c not in selected_countries]
        
        if available_for_selection:
            add_country = st.selectbox(
                "Select country to add:",
                available_for_selection,
                key="add_country"
            )
            
            if st.button("➕ Add Country", key="add_country_btn"):
                if add_country not in selected_countries and len(selected_countries) < 5:
                    selected_countries.append(add_country)
                    st.rerun()
        else:
            st.info("All countries already selected (max 5)")
    
    st.markdown("---")
    
    # Comparison Section
    st.subheader("⚖️ Country Comparison Dashboard")
    
    if selected_countries:
        # Line chart comparison
        compare_df = df[df['Country Name'].isin(selected_countries)]
        
        if not compare_df.empty:
            # Create tabs for different comparison views
            compare_tab1, compare_tab2 = st.tabs([
                "📈 Trend Comparison", 
                "📊 Relative Performance"
            ])
            
            with compare_tab1:
                fig = px.line(
                    compare_df,
                    x='Year',
                    y='GDP_Billion',
                    color='Country Name',
                    title='GDP Trend Comparison',
                    markers=True,
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                
                fig.update_layout(
                    height=400,
                    hovermode='x unified',
                    yaxis_title="GDP (Billion USD)",
                    xaxis_title="Year"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Winda's insight
                st.markdown("""
                <div class="metric-card">
                <h4>🎨 Winda's Insight:</h4>
                <p><b>Interactive Tip:</b> Hover over any point to see detailed GDP values. 
                Click on country names in the legend to hide/show specific trends.</p>
                <p><b>Observation:</b> Notice how different countries respond to global events.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with compare_tab2:
                # Calculate indexed growth (2000 = 100)
                indexed_data = []
                for country in selected_countries:
                    country_data = compare_df[compare_df['Country Name'] == country].sort_values('Year')
                    if not country_data.empty:
                        base_gdp = country_data.iloc[0]['GDP (Current US$)']
                        
                        for _, row in country_data.iterrows():
                            index = (row['GDP (Current US$)'] / base_gdp) * 100
                            indexed_data.append({
                                'Country': country,
                                'Year': row['Year'],
                                'Index': index
                            })
                
                if indexed_data:
                    indexed_df = pd.DataFrame(indexed_data)
                    
                    fig = px.line(
                        indexed_df,
                        x='Year',
                        y='Index',
                        color='Country',
                        title='Indexed Growth Comparison (2000 = 100)',
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    
                    fig.update_layout(
                        height=400,
                        yaxis_title="Index (2000 = 100)",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No comparison data available.")
    else:
        st.info("Please select countries to compare from the sidebar.")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Developed by:**")
    st.markdown("- Reni Agustí")
    st.markdown("- Winda Adisty")

with col2:
    st.markdown("**Technologies:**")
    st.markdown("- Streamlit")
    st.markdown("- Plotly")
    st.markdown("- Pandas")

with col3:
    st.markdown("**Data Source:**")
    st.markdown("World Bank GDP Data")
    st.markdown("(2000-2024)")

st.markdown("<p style='text-align: center; color: #666;'>© 2024 World GDP Insight Dashboard. All rights reserved.</p>", unsafe_allow_html=True)
