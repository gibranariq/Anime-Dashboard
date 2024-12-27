# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df = pd.read_csv('data/top_animes_after_cleaning.csv')

#######################
# Sidebar
# Sidebar Filters
with st.sidebar:
    st.title('Anime Dashboard Filters')

    # Filter berdasarkan genre utama (Themes)
    genre_list = sorted(set(theme.strip() for themes in df['Themes'].dropna() for theme in themes.strip('[]').replace("'", "").split(',')))
    selected_genre = st.selectbox('Select a Genre', genre_list)
    filtered_data = df[df['Themes'].str.contains(selected_genre, na=False)]

    # Filter berdasarkan demografi (Demographics)
    demographic_list = sorted(set(demo.strip() for demos in df['Demographics'].dropna() for demo in demos.strip('[]').replace("'", "").split(',')))
    selected_demo = st.selectbox('Select a Demographic', demographic_list)
    filtered_data = filtered_data[filtered_data['Demographics'].str.contains(selected_demo, na=False)]

    # Filter berdasarkan jumlah favorit (Favorites)
    popularity_list = sorted(filtered_data['Favorites'].dropna().unique(), reverse=True)
    selected_popularity = st.slider('Minimum Favorites', min_value=min(popularity_list), max_value=max(popularity_list), value=min(popularity_list))
    filtered_data = filtered_data[filtered_data['Favorites'] >= selected_popularity]

    # Filter berdasarkan tipe (TV, Movie, dll.)
    type_list = df['Type'].dropna().unique()
    selected_type = st.selectbox('Select a Type', type_list)
    filtered_data = filtered_data[filtered_data['Type'] == selected_type]

# Main Panel
st.title("Anime Analytics Dashboard")

# 1. Top Metrics
st.markdown("### Top Metrics")
col1, col2, col3 = st.columns(3)

if not filtered_data.empty:
    top_anime = filtered_data.nlargest(1, 'Favorites').iloc[0]
    col1.metric(label="Top Anime", value=top_anime['Name'])
    col2.metric(label="Total Favorites (Filtered)", value=filtered_data['Favorites'].sum())
    col3.metric(label="Total Episodes (Filtered)", value=filtered_data['Episodes'].sum())
else:
    col1.metric(label="Top Anime", value="No Data")
    col2.metric(label="Total Favorites (Filtered)", value=0)
    col3.metric(label="Total Episodes (Filtered)", value=0)

# 2. Bar Chart - Top Anime by Favorites
st.markdown("### Top Anime by Favorites")
if not filtered_data.empty:
    top_favorites = filtered_data.nlargest(10, 'Favorites')
    bar_chart = alt.Chart(top_favorites).mark_bar().encode(
        x=alt.X('Favorites:Q', title='Favorites'),
        y=alt.Y('Name:N', sort='-x', title='Anime Name'),
        color=alt.Color('Favorites:Q', scale=alt.Scale(scheme='blues'), legend=None)
    ).properties(width=700, height=400)
    st.altair_chart(bar_chart, use_container_width=True)
else:
    st.write("No data available for bar chart.")

# 3. Pie Chart - Distribution of Demographics
st.markdown("### Demographics Distribution")
if not filtered_data.empty:
    demo_counts = filtered_data['Demographics'].value_counts()
    pie_chart = px.pie(
        names=demo_counts.index,
        values=demo_counts.values,
        title='Demographics Distribution',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(pie_chart, use_container_width=True)
else:
    st.write("No data available for pie chart.")

# 4. Scatter Plot - Favorites vs Episodes
st.markdown("### Favorites vs Episodes")
if not filtered_data.empty:
    scatter_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
        x=alt.X('Episodes:Q', title='Number of Episodes'),
        y=alt.Y('Favorites:Q', title='Favorites'),
        tooltip=['Name', 'Episodes', 'Favorites'],
        color=alt.Color('Favorites:Q', scale=alt.Scale(scheme='viridis'), legend=None)
    ).interactive().properties(width=700, height=400)
    st.altair_chart(scatter_plot, use_container_width=True)
else:
    st.write("No data available for scatter plot.")

# 5. Heatmap - Themes and Demographics
st.markdown("### Heatmap of Favorites by Themes and Demographics")
if not filtered_data.empty:
    heatmap = alt.Chart(filtered_data).mark_rect().encode(
        y=alt.Y('Themes:N', title='Themes'),
        x=alt.X('Demographics:N', title='Demographics'),
        color=alt.Color('Favorites:Q', title='Favorites', scale=alt.Scale(scheme='plasma')),
        tooltip=['Themes', 'Demographics', 'Favorites']
    ).properties(width=700, height=400)
    st.altair_chart(heatmap, use_container_width=True)
else:
    st.write("No data available for heatmap.")

# 6. Data Table
st.markdown("### Filtered Anime Data")
st.dataframe(filtered_data[['Name', 'Favorites', 'Episodes', 'Type', 'Demographics', 'Themes']], width=800, height=400)

# About Section
st.markdown("### About This Dashboard")
st.write("""
- **Data Source**: Provided anime dataset.
- **Visualizations**: Various charts to analyze anime data based on genres, demographics, and popularity.
- **Features**: Interactive filters for Genres, Demographics, Favorites, and Type.
""")

