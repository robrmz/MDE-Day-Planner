import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MDE Visualizer",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CALCULATION FUNCTIONS (No changes needed here) ---
def calculate_mde(confidence_level, power, baseline_rate, sample_size):
    """Calculate Minimum Detectable Effect (as a percentage)."""
    if baseline_rate <= 0 or sample_size <= 0:
        return np.inf
    alpha = 1 - confidence_level
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    term1 = z_alpha + z_beta
    term2 = np.sqrt(2 * baseline_rate * (1 - baseline_rate) / sample_size)
    mde_proportion = (term1 * term2) / baseline_rate
    return mde_proportion * 100

# --- INTERACTIVE PLOTTING FUNCTION ---
def create_interactive_plot(df):
    """Creates a clean, interactive Plotly chart with rich hover data."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Day'],
        y=df['MDE (%)'],
        customdata=df['Sample Size Per Variation'],
        mode='lines',
        name='MDE Curve',
        line=dict(color='royalblue', width=3),
        hovertemplate=(
            "<b>Day %{x}</b><br><br>" +
            "Minimum Detectable Effect: <b>%{y:.2f}%</b><br>" +
            "Sample Size per Variation: <b>%{customdata:,.0f}</b>" +
            "<extra></extra>"
        )
    ))

    fig.add_trace(go.Scatter(
        x=df['Day'],
        y=df['MDE (%)'],
        fill='tozeroy',
        mode='none',
        name='Area',
        fillcolor='rgba(70, 130, 180, 0.1)',
        hoverinfo='none'
    ))

    fig.update_layout(
        title={
            'text': "<b>Minimum Detectable Effect vs. Test Duration</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Test Duration (Days)",
        yaxis_title="Minimum Detectable Effect (%)",
        hovermode="x unified",
        showlegend=False,
        template="plotly_white",
        height=500,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    return fig

# --- MAIN APP ---
def main():
    # --- SIDEBAR FOR USER INPUTS ---
    with st.sidebar:
        st.title("🧪 Test Parameters")
        st.markdown("Adjust inputs to visualize the MDE curve.")
        
        st.header("Confidence & Power")
        confidence_level = 1 - st.slider(label="Significance Level (α)", min_value=0.01, max_value=0.20, value=0.1, step=0.01, format="%.2f")
        power = st.slider(label="Statistical Power (1-β)", min_value=0.70, max_value=0.99, value=0.80, step=0.01)

        st.header("Metric & Traffic")
        
        # CHANGED: Input is now a percentage.
        baseline_rate_percent = st.number_input(
            label="Baseline Conversion Rate (%)",
            min_value=0.01,
            max_value=99.99,
            value=5.0,
            step=0.1,
            format="%.2f"
        )
        # Convert percentage to proportion for the calculation functions.
        baseline_rate = baseline_rate_percent / 100.0

        daily_traffic = st.number_input(label="Daily Users per Variation", min_value=10, value=10000, step=10)

        st.header("Projection Period")
        max_days = st.slider(label="Days to Project", min_value=1, max_value=90, value=21, step=1)

    # --- CORE CALCULATIONS & DATAFRAME CREATION ---
    days_array = np.arange(1, max_days + 1)
    n_values = days_array * daily_traffic
    
    df = pd.DataFrame({
        'Day': days_array,
        'Sample Size Per Variation': n_values,
        'Total Sample Size': n_values * 2,
    })
    
    # The 'baseline_rate' variable passed here is now the correct proportion.
    df['MDE (%)'] = df['Sample Size Per Variation'].apply(
        lambda n: calculate_mde(confidence_level, power, baseline_rate, n)
    )

    # --- MAIN CONTENT AREA ---
    st.title("📈 MDE Visualizer")
    st.markdown("An interactive tool to explore the relationship between test duration, sample size, and detectable effect. **Hover over the chart for details.**")

    fig = create_interactive_plot(df)
    st.plotly_chart(fig, use_container_width=True)

    # --- SUMMARY STATEMENT ---
    last_day = df['Day'].iloc[-1]
    last_mde = df['MDE (%)'].iloc[-1]
    st.markdown(
        f"🗓️ <b>At day {last_day}</b>, you would be able to detect a <b>{last_mde:.2f}%</b> difference.",
        unsafe_allow_html=True
    )
    # Table
    st.markdown("---")
    st.subheader("Day-by-Day Data")
    
    st.dataframe(
        df.style.format({
            'MDE (%)': '{:.2f}',
            'Sample Size Per Variation': '{:,.0f}',
            'Total Sample Size': '{:,.0f}'
        }),
        height=350,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Download Data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"mde_projection_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.caption("✨ Built by RR")


if __name__ == "__main__":
    main()