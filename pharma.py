import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Page Configuration
st.set_page_config(page_title="📊 Sales Analytics BI Assistant", layout="wide")

# Load and Prepare Data
@st.cache_data
def load_data():
    df = pd.read_excel(r"data/Sales_data (1).xlsx")
    df['Month'] = pd.to_datetime(df['Order Date']).dt.to_period('M')
    return df

# Query Handler
def process_query(query, data):
    query = query.lower()
    fig, ax = plt.subplots(figsize=(10, 6))

    if "top" in query and "product" in query:
        n = int(''.join(filter(str.isdigit, query))) if any(c.isdigit() for c in query) else 10
        result = data.groupby('Item ID')['Total Price'].sum().nlargest(n)
        result.plot(kind='bar', ax=ax, color='blue')
        plt.title(f'Top {n} Selling Products')
        plt.xlabel('Item ID')
        plt.ylabel('Total Revenue')

    elif "monthly" in query and "sales" in query:
        result = data.groupby('Month')['Total Price'].sum()
        result.plot(marker='o', ax=ax, color='green')
        plt.title('Monthly Sales Trends')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)

    elif "customer" in query:
        n = int(''.join(filter(str.isdigit, query))) if any(c.isdigit() for c in query) else 5
        result = data.groupby('Customer ID')['Total Price'].sum().nlargest(n)
        result.plot(kind='bar', ax=ax, color='orange')
        plt.title(f'Top {n} Customers by Sales')
        plt.xlabel('Customer ID')
        plt.ylabel('Total Sales')

    elif "return" in query or "ship" in query:
        result = data[['Qty Shipped', 'Qty Returned']].sum()
        result.plot(kind='bar', ax=ax, color='Blue', log=True)  # Log scale for better visibility
        plt.title('Shipped vs Returned Quantities')
        plt.xlabel('Category')
        plt.ylabel('Quantity (Log Scale)')

        # Add value labels to bars
        for i, value in enumerate(result):
            ax.text(i, value, f'{value:.2f}', ha='center', va='bottom', fontsize=10)

    else:
        return "Query not understood", None, None

    return plt, result

# Plot Download Helper
def get_plot_download_link(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Main UI
def main():
    st.title("📊 Sales Analytics BI Assistant ")
    st.write("Ask me anything about your sales data!")

    # Load Data
    try:
        data = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Query Input
    query = st.text_input("Enter your question:", placeholder="e.g., 'Show me top 10 selling products'")

    if query:
        with st.spinner('Analyzing your request...'):
            fig, result = process_query(query, data)

            if result is not None:
                # Tabs for Visualization & Data
                tab1, tab2 = st.tabs(["📈 Visualization", "📋 Data"])
                with tab1:
                    st.pyplot(fig)
                    buf = get_plot_download_link(fig)
                    st.download_button("Download Plot", data=buf, file_name="plot.png", mime="image/png")

                with tab2:
                    st.dataframe(result)
                    csv = result.to_csv().encode('utf-8')
                    st.download_button("Download Data", data=csv, file_name="data.csv", mime="text/csv")

            else:
                st.warning("I couldn't understand your question. Please try rephrasing it.")

    # Sidebar Examples
    with st.sidebar:
        st.subheader("Example Questions")
        st.write("1. What are the top 10 selling products?")
        st.write("2.Show me monthly sales trends")
        st.write("3.Who are the top 5 customers?")
        st.write("4.Compare shipped vs returned quantities")

if __name__ == "__main__":
    main()
