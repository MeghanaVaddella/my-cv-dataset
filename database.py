import streamlit as st
import pandas as pd
import requests
import networkx as nx
import matplotlib.pyplot as plt

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="PPI Network Database", layout="wide")

# ---- SIDEBAR NAVIGATION ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Data", "Visualization Tool", "GitHub Data Edit"])

# ---- LOAD DATA FROM GITHUB ----
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://raw.githubusercontent.com/MeghanaVaddella/my-cv-dataset/main/cleaned_interactions.csv"
    try:
        df = pd.read_csv(url)
        st.success("✅ Data successfully loaded!")
        return df
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return pd.DataFrame()

df = load_data()

# ---- CREATE NETWORKX GRAPH ----
def create_ppi_graph(data):
    G = nx.Graph()
    for _, row in data.iterrows():
        G.add_edge(str(row["Protein_A"]), str(row["Protein_B"]))
    return G

ppi_graph = create_ppi_graph(df)

# ---- HOME PAGE ----
if page == "Home":
    st.title("Protein-Protein Interactions of Neurodegenerative Disorders")
    st.write("""
    This database provides curated protein-protein interaction (PPI) data relevant to neurodegenerative diseases.
    It integrates data from STRING, BioGRID, and IntAct, with functional annotations and network topology analysis.
    """)

    # Search bars for proteins
    col1, col2 = st.columns(2)
    with col1:
        protein_a = st.text_input("Search for Protein A:")
    with col2:
        protein_b = st.text_input("Search for Protein B:")

    # Search and display results
    if protein_a or protein_b:
        filtered_df = df[
            (df.iloc[:, 0].astype(str).str.contains(protein_a, case=False, na=False)) |
            (df.iloc[:, 1].astype(str).str.contains(protein_b, case=False, na=False))
        ]
        
        st.write(f"### Search Results for '{protein_a}' and '{protein_b}'")
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.write("### No interactions found")

# ---- DATA PAGE ----
elif page == "Data":
    st.title("PPI Data")
    st.write("### Full Protein-Protein Interaction Data")
    st.dataframe(df)
    st.download_button(
        "Download Processed Data", df.to_csv(index=False), file_name="PPI_data.csv", mime="text/csv"
    )

# ---- VISUALIZATION TOOL PAGE ----
elif page == "Visualization Tool":
    st.title("Visualization Tool")
    st.write("### Network Visualization of PPI Data (Pastel Theme)")

    if df.empty:
        st.warning("⚠ No data available to visualize. Please check the dataset.")
    else:
        # ✅ Generate NetworkX Graph Layout
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(ppi_graph, seed=42, k=0.5)  # k=0.5 reduces overlap
        node_sizes = [ppi_graph.degree(n) * 300 for n in ppi_graph.nodes()]  # Bigger nodes for high-degree proteins

        # ✅ Pastel Color Palette
        pastel_colors = [
            "#FFB6C1",  # Light Pink
            "#FFDAB9",  # Peach
            "#B0E0E6",  # Powder Blue
            "#98FB98",  # Pale Green
            "#E6E6FA",  # Lavender
            "#F0E68C",  # Khaki
            "#DDA0DD",  # Plum
        ]
        
        node_color_map = {node: pastel_colors[i % len(pastel_colors)] for i, node in enumerate(ppi_graph.nodes())}
        edge_color = "#C0C0C0"  # Light Gray edges

        nx.draw(
            ppi_graph, pos, with_labels=True, node_size=node_sizes,
            node_color=[node_color_map[n] for n in ppi_graph.nodes()],  # Apply pastel colors
            edge_color=edge_color, font_size=10
        )

        # ✅ Display Graph in Streamlit
        st.pyplot(plt)

# ---- GITHUB EDIT PAGE ----
elif page == "GitHub Data Edit":
    st.title("GitHub Data Edit")
    st.markdown("[Edit Data on GitHub](https://github.com/MeghanaVaddella/my-cv-dataset/edit/main/cleaned_interactions.csv)")

# ---- REMOVE STREAMLIT BRANDING ----
st.markdown("""<style> footer {visibility: hidden;} </style>""", unsafe_allow_html=True)
