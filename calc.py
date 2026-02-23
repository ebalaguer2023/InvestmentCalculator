import streamlit as st
import pandas as pd

st.set_page_config(page_title="Investment Growth Simulator", page_icon="📈")

st.title("📈 Investment Growth Simulator")
st.write("Compound interest calculator with initial capital and periodic contributions")

# ---------------- INPUTS ----------------

initial_capital = st.number_input(
    "Initial Investment",
    min_value=0.0,
    value=10000.0,
    step=1000.0
)

periodic_contribution = st.number_input(
    "Periodic Contribution (same frequency as compounding)",
    min_value=0.0,
    value=0.0,
    step=100.0
)

annual_rate = st.number_input(
    "Nominal Annual Interest Rate (%)",
    min_value=0.0,
    value=10.0,
    step=0.5
)

frequencies = {
    "Annually (once per year)": 1,
    "Semiannually (twice per year)": 2,
    "Quarterly (4 times per year)": 4,
    "Monthly (12 times per year)": 12
}

selected_frequency = st.selectbox(
    "Compounding Frequency",
    options=list(frequencies.keys())
)

m = frequencies[selected_frequency]

years = st.number_input(
    "Investment Period (years)",
    min_value=1,
    value=5,
    step=1
)

# ---------------- CALCULATIONS ----------------

i = annual_rate / 100
r = i / m
n = m * years

# Future value of initial investment
fv_initial = initial_capital * (1 + r) ** n

# Future value of periodic contributions (ordinary annuity)
if r > 0:
    fv_contributions = periodic_contribution * (((1 + r) ** n - 1) / r)
else:
    fv_contributions = periodic_contribution * n

future_value = fv_initial + fv_contributions

total_contributed = initial_capital + periodic_contribution * n
interest_earned = future_value - total_contributed

# ---------------- RESULTS ----------------

st.markdown("---")
st.subheader("Final Results")

st.success(f"Total Future Value: ${future_value:,.2f}")

st.write(f"• Total Amount Contributed: ${total_contributed:,.2f}")
st.write(f"• Total Interest Earned: ${interest_earned:,.2f}")

# ---------------- GROWTH CHART ----------------

values = []
year_list = list(range(0, years + 1))

for t in year_list:
    n_temp = m * t
    
    fv_initial_temp = initial_capital * (1 + r) ** n_temp
    
    if r > 0:
        fv_contributions_temp = periodic_contribution * (((1 + r) ** n_temp - 1) / r)
    else:
        fv_contributions_temp = periodic_contribution * n_temp
        
    values.append(fv_initial_temp + fv_contributions_temp)

df = pd.DataFrame({
    "Year": year_list,
    "Accumulated Value": values
})

st.markdown("---")
st.subheader("Investment Growth Over Time")

st.line_chart(df.set_index("Year"))

st.dataframe(df)