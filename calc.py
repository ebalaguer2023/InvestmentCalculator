import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(
    page_title="Investment Growth Simulator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Investment Growth Simulator")
st.caption("Compound interest calculator with contributions, inflation and scenario comparison")

# ---------------- SIDEBAR ----------------

st.sidebar.header("Scenario A")

initial_capital = st.sidebar.number_input("Initial Investment ($)", 0.0, 1_000_000_000.0, 10000.0)
periodic_contribution = st.sidebar.number_input("Periodic Contribution ($)", 0.0, 1_000_000_000.0, 500.0)
annual_rate = st.sidebar.number_input("Nominal Annual Interest Rate (%)", 0.0, 100.0, 10.0)
inflation_rate = st.sidebar.number_input("Annual Inflation Rate (%)", 0.0, 100.0, 3.0)
years = st.sidebar.number_input("Investment Period (years)", 1, 100, 10)

frequencies = {
    "Annually (1)": 1,
    "Semiannually (2)": 2,
    "Quarterly (4)": 4,
    "Monthly (12)": 12
}

selected_frequency = st.sidebar.selectbox("Compounding Frequency", list(frequencies.keys()))
m = frequencies[selected_frequency]

annuity_type = st.sidebar.radio(
    "Contribution Timing",
    ["End of Period (Ordinary Annuity)", "Beginning of Period (Annuity Due)"]
)

# Scenario B toggle
compare = st.sidebar.checkbox("Enable Scenario Comparison")

if compare:
    st.sidebar.markdown("---")
    st.sidebar.header("Scenario B")
    annual_rate_b = st.sidebar.number_input("Scenario B Interest Rate (%)", 0.0, 100.0, 7.0)
else:
    annual_rate_b = None


# ---------------- RETIREMENTS ----------------    
st.sidebar.markdown("---")
st.sidebar.header("Retirement Phase")

enable_retirement = st.sidebar.checkbox("Enable Retirement Simulation")

if enable_retirement:
    retirement_years = st.sidebar.number_input("Years in Retirement", 1, 60, 25)
    annual_withdrawal = st.sidebar.number_input("Annual Withdrawal ($)", 0.0, 1_000_000_000.0, 30000.0)

# ---------------- MONTE CARLO ----------------        
st.sidebar.markdown("---")
st.sidebar.header("Monte Carlo Simulation")

use_mc = st.sidebar.checkbox("Enable Monte Carlo Simulation")

if use_mc:
    
    
    st.markdown("## 🎲 Monte Carlo Simulation")


    expected_return = st.sidebar.number_input("Expected Annual Return (%)", 0.0, 100.0, 10.0)
    volatility = st.sidebar.number_input("Annual Volatility (%)", 0.0, 100.0, 15.0)
    simulations = st.sidebar.slider("Number of Simulations", 100, 2000, 500)
    
    mu = expected_return / 100
    sigma = volatility / 100

    success_count = 0
    final_values = []
    depletion_years = []

    for s in range(simulations):

        value = initial_capital

        # ----- ACCUMULATION PHASE -----
        for year in range(years):
            annual_contribution = periodic_contribution * m
            random_return = np.random.normal(mu, sigma)
            value = (value + annual_contribution) * (1 + random_return)

        # ----- RETIREMENT PHASE -----
        survived = True

        if enable_retirement:
            for r_year in range(retirement_years):
                random_return = np.random.normal(mu, sigma)
                value = (value - annual_withdrawal) * (1 + random_return)

                if value <= 0:
                    depletion_years.append(r_year)
                    survived = False
                    break

        if survived:
            success_count += 1

        final_values.append(max(value, 0))

    success_rate = (success_count / simulations) * 100

    # -------- Metrics --------

    col1, col2, col3 = st.columns(3)

    col1.metric("Probability of Success", f"{success_rate:.1f}%")
    col2.metric("Average Final Value", f"${np.mean(final_values):,.2f}")
    col3.metric("Median Final Value", f"${np.median(final_values):,.2f}")

    # -------- Histogram --------
    p10 = np.percentile(final_values, 10)
    p50 = np.percentile(final_values, 50)
    p90 = np.percentile(final_values, 90)

    st.markdown("### 📊 Distribution Percentiles")

    col1, col2, col3 = st.columns(3)
    col1.metric("P10 (Conservative)", f"${p10:,.2f}")
    col2.metric("P50 (Median)", f"${p50:,.2f}")
    col3.metric("P90 (Optimistic)", f"${p90:,.2f}")
    


    fig, ax = plt.subplots()
    ax.hist(final_values, bins=40)
    ax.axvline(p10, linestyle="--")
    ax.axvline(p50, linestyle="--")
    ax.axvline(p90, linestyle="--")
    ax.set_title("Monte Carlo Distribution")
    st.pyplot(fig)

    # -------- If retirement enabled --------

    if enable_retirement and len(depletion_years) > 0:
        avg_depletion = np.mean(depletion_years)
        st.warning(f"Average portfolio depletion occurred after {avg_depletion:.1f} retirement years.")


    # -------- Safe withdrawal with Monte Carlo--------    
    # Safe Withdrawal Rate estimation
    if enable_retirement:
        swr_estimate = 0
        test_rates = np.linspace(0.02, 0.08, 25)  # 2% to 8%
        
        for rate in test_rates:
            success_count = 0
            
            for s in range(simulations):
                value = initial_capital
                
                # accumulation
                for year in range(years):
                    annual_contribution = periodic_contribution * m
                    random_return = np.random.normal(mu, sigma)
                    value = (value + annual_contribution) * (1 + random_return)
                
                withdrawal = value * rate
                
                survived = True
                for r_year in range(retirement_years):
                    random_return = np.random.normal(mu, sigma)
                    value = (value - withdrawal) * (1 + random_return)
                    if value <= 0:
                        survived = False
                        break
                
                if survived:
                    success_count += 1
            
            success_rate_test = success_count / simulations
            
            if success_rate_test >= 0.85:  # 85% success threshold
                swr_estimate = rate
        
        st.markdown("### 🎯 Estimated Safe Withdrawal Rate")
        st.success(f"Safe Withdrawal Rate (≈85% success): {swr_estimate*100:.2f}%")
# ---------------- CALC FUNCTION ----------------

def simulate(rate):
    i = rate / 100
    r = i / m
    n = m * years
    inflation = inflation_rate / 100

    values = []
    contributions = []
    interest = []
    real_values = []

    for t in range(0, years + 1):
        n_temp = m * t

        fv_initial = initial_capital * (1 + r) ** n_temp

        if r > 0:
            fv_contrib = periodic_contribution * (((1 + r) ** n_temp - 1) / r)
        else:
            fv_contrib = periodic_contribution * n_temp

        if "Beginning" in annuity_type:
            fv_contrib *= (1 + r)

        total = fv_initial + fv_contrib
        contrib_total = initial_capital + periodic_contribution * n_temp
        interest_total = total - contrib_total

        # Adjust for inflation
        real_total = total / ((1 + inflation) ** t)

        values.append(total)
        contributions.append(contrib_total)
        interest.append(interest_total)
        real_values.append(real_total)

    df = pd.DataFrame({
        "Year": range(0, years + 1),
        "Total Value": values,
        "Total Contributions": contributions,
        "Interest Earned": interest,
        "Real Value (Inflation Adjusted)": real_values
    })

    return df

# Run simulation
df_a = simulate(annual_rate)

if compare:
    df_b = simulate(annual_rate_b)

# ---------------- METRICS ----------------

st.markdown("## 📊 Investment Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Future Value (Scenario A)", f"${df_a['Total Value'].iloc[-1]:,.2f}")
col2.metric("Interest Earned", f"${df_a['Interest Earned'].iloc[-1]:,.2f}")
col3.metric("Inflation Adjusted Value", f"${df_a['Real Value (Inflation Adjusted)'].iloc[-1]:,.2f}")

# 4% Rule
four_percent_income = df_a["Total Value"].iloc[-1] * 0.04

st.markdown("### 📉 4% Rule Estimate")
st.info(f"Estimated Sustainable Annual Withdrawal (4% rule): ${four_percent_income:,.2f}")

# ---------------- AREA CHART ----------------

st.markdown("## 📈 Growth Breakdown")

area_df = df_a.set_index("Year")[["Total Contributions", "Interest Earned"]]
st.area_chart(area_df)

# ---------------- SCENARIO COMPARISON ----------------

if compare:
    st.markdown("## ⚖ Scenario Comparison")

    compare_df = pd.DataFrame({
        "Scenario A": df_a["Total Value"],
        "Scenario B": df_b["Total Value"]
    }, index=df_a["Year"])

    st.line_chart(compare_df)

# ---------------- DOWNLOAD EXCEL ----------------

st.markdown("## 📥 Download Results")

output = BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df_a.to_excel(writer, sheet_name="Scenario A", index=False)
    if compare:
        df_b.to_excel(writer, sheet_name="Scenario B", index=False)

st.download_button(
    label="Download Excel File",
    data=output.getvalue(),
    file_name="investment_simulation.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------- TABLE ----------------

st.markdown("## 📋 Detailed Results")
st.dataframe(df_a)

