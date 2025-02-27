import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def main():
    st.title("Days to detect (MDE Planner)")

    # 1. User Inputs
    alpha = st.number_input("Significance Level (alpha)", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
    power = st.number_input("Statistical Power", value=0.8, min_value=0.0, max_value=1.0, step=0.01)
    p = st.number_input("Baseline Rate (e.g. 0.1159 for 11.59%)", value=0.1159, min_value=0.0, max_value=1.0, step=0.001, format="%.4f")
    step_size = st.number_input("Visits per Day (Step Size)", value=7989, min_value=1, step=1)
    max_days = st.number_input("Days to Look into the Future", value=21, min_value=1, step=1)

    # 2. Optional Title Modifiers
    plot_title = st.text_input("Main Title for the Plot", "Approximated Minimal Detectable Effect by Day")
    plot_subtitle = st.text_input(
        "Subtitle for the Plot",
        f"Based on A2C Rate baseline {p*100:.2f}%, Daily group traffic of {step_size} and {power*100:.0f}% power"
    )

    # 3. Calculations
    z_alpha = norm.ppf(1 - alpha / 2)  # For alpha=0.1, e.g., z_alpha ~ 1.645
    z_beta = norm.ppf(power)          # For power=0.8,  z_beta ~ 0.84

    # We'll calculate MDE across days 1 through max_days
    # so the total sample size for day i is i * step_size
    days_array = np.arange(1, max_days + 1)
    n_values = days_array * step_size

    # MDE in percentage terms
    MDE_values = ((z_alpha + z_beta) * np.sqrt(2 * p * (1 - p) / n_values) / p) * 100

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(n_values, MDE_values, marker='o', label='MDE vs Sample Size')
    
    # Create a list of day labels for the x-axis
    day_labels = [f"Day {i}" for i in days_array]

    # Set the x-ticks to be the sample size points (n_values),
    # and the labels to "Day 1", "Day 2", etc.
    ax.set_xticks(n_values)
    ax.set_xticklabels(day_labels, rotation=45)

    ax.set_xlabel("Days")
    ax.set_ylabel("MDE (%)")
    ax.grid(True)
    ax.legend()
    
    # Titles
    # suptitle isn't directly supported in Streamlit, so we can place it in the figure text
    plt.suptitle(plot_title)
    ax.set_title(plot_subtitle, fontsize=10)

    fig.tight_layout()
    st.pyplot(fig)

if __name__ == "__main__":
    main()
