import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Tính Lãi Vay Mua Nhà", layout="wide")

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        padding: 20px 0;
    }
    .scenario-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-box {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">💰 BẢNG TÍNH LÃI VAY MUA NHÀ 🏠</div>', unsafe_allow_html=True)

# Sidebar - Input parameters
with st.sidebar:
    st.header("⚙️ Thông Tin Vốn")
    
    current_assets = st.number_input(
        "Tổng tiền hiện có (VNĐ)", 
        value=2_865_000_000, 
        step=10_000_000,
        format="%d"
    )
    
    projected_2026 = st.number_input(
        "Dự tính đến khi mua (VNĐ)", 
        value=3_615_000_000, 
        step=10_000_000,
        format="%d"
    )
    
    rental_income = st.number_input(
        "Thu nhập cho thuê/tháng (VNĐ)", 
        value=8_000_000, 
        step=500_000,
        format="%d"
    )
    
    st.divider()
    st.header("📊 Thông Tin Lãi Suất")
    
    # Lãi suất ưu đãi
    promo_rate = st.number_input(
        "Lãi suất ưu đãi (%/năm)", 
        value=7.0, 
        step=0.1,
        format="%.1f"
    )
    
    promo_months = st.number_input(
        "Thời gian ưu đãi (tháng)", 
        value=12, 
        step=6,
        min_value=0
    )
    
    # Lãi suất thả nổi
    regular_rate = st.number_input(
        "Lãi suất thả nổi (%/năm)", 
        value=10.0, 
        step=0.1,
        format="%.1f"
    )
    
    loan_term_years = st.number_input(
        "Thời gian vay (năm)", 
        value=15, 
        step=1,
        min_value=1,
        max_value=30
    )

# Hàm tính lãi giảm dần
def calculate_reducing_balance_loan(principal, promo_rate, regular_rate, promo_months, total_months):
    monthly_principal = principal / total_months
    schedule = []
    remaining_balance = principal
    
    for month in range(1, total_months + 1):
        # Áp dụng lãi suất ưu đãi hoặc lãi suất thả nổi
        if month <= promo_months:
            monthly_rate = promo_rate / 100 / 12
        else:
            monthly_rate = regular_rate / 100 / 12
        
        monthly_interest = remaining_balance * monthly_rate
        monthly_payment = monthly_principal + monthly_interest
        remaining_balance -= monthly_principal
        
        schedule.append({
            'Tháng': month,
            'Dư nợ đầu kỳ': remaining_balance + monthly_principal,
            'Tiền gốc': monthly_principal,
            'Tiền lãi': monthly_interest,
            'Tổng trả': monthly_payment,
            'Dư nợ cuối kỳ': remaining_balance
        })
    
    return schedule

# Định nghĩa các kịch bản
scenarios = [
    {
        'name': 'KB1: Chung cư TH 1.1',
        'price': 4_500_000_000,
        'type': 'Ở luôn',
        'rental': False,
        'color': '#3B82F6'
    },
    {
        'name': 'KB1: Chung cư TH 1.2',
        'price': 5_000_000_000,
        'type': 'Ở luôn',
        'rental': False,
        'color': '#8B5CF6'
    },
    {
        'name': 'KB2: Nhà đất TH 2.1',
        'price': 7_000_000_000,
        'type': 'Cho thuê',
        'rental': True,
        'color': '#10B981'
    },
    {
        'name': 'KB2: Nhà đất TH 2.2',
        'price': 7_000_000_000,
        'type': 'Ở luôn',
        'rental': False,
        'color': '#F59E0B'
    }
]

# Tabs cho từng kịch bản
tabs = st.tabs([s['name'] for s in scenarios])

for idx, (tab, scenario) in enumerate(zip(tabs, scenarios)):
    with tab:
        loan_amount = scenario['price'] - projected_2026
        total_months = loan_term_years * 12
        
        # Tính toán lịch trả nợ
        schedule = calculate_reducing_balance_loan(
            loan_amount, 
            promo_rate, 
            regular_rate, 
            promo_months, 
            total_months
        )
        
        df = pd.DataFrame(schedule)
        total_interest = df['Tiền lãi'].sum()
        total_payment = loan_amount + total_interest
        
        # Hiển thị thông tin tổng quan
        st.markdown(f"### 🏘️ {scenario['name']} - {scenario['type']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 Giá nhà", f"{scenario['price']:,.0f} VNĐ")
        
        with col2:
            st.metric("📊 Số tiền vay", f"{loan_amount:,.0f} VNĐ")
        
        with col3:
            st.metric("💰 Tổng lãi phải trả", f"{total_interest:,.0f} VNĐ")
        
        with col4:
            st.metric("💳 Tổng tiền trả", f"{total_payment:,.0f} VNĐ")
        
        # Thông tin chi tiết tháng đầu và cuối
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📅 Tháng đầu tiên")
            first_month = df.iloc[0]
            st.write(f"**Tiền gốc:** {first_month['Tiền gốc']:,.0f} VNĐ")
            st.write(f"**Tiền lãi:** {first_month['Tiền lãi']:,.0f} VNĐ")
            st.write(f"**Tổng trả:** {first_month['Tổng trả']:,.0f} VNĐ")
            if scenario['rental']:
                net_payment = first_month['Tổng trả'] - rental_income
                st.write(f"**Thực trả (sau thuê):** {net_payment:,.0f} VNĐ")
        
        with col2:
            st.markdown("#### 📅 Tháng cuối cùng")
            last_month = df.iloc[-1]
            st.write(f"**Tiền gốc:** {last_month['Tiền gốc']:,.0f} VNĐ")
            st.write(f"**Tiền lãi:** {last_month['Tiền lãi']:,.0f} VNĐ")
            st.write(f"**Tổng trả:** {last_month['Tổng trả']:,.0f} VNĐ")
            if scenario['rental']:
                net_payment = last_month['Tổng trả'] - rental_income
                st.write(f"**Thực trả (sau thuê):** {net_payment:,.0f} VNĐ")
        
        with col3:
            st.markdown("#### 📊 Trung bình/tháng")
            avg_payment = df['Tổng trả'].mean()
            st.write(f"**Trung bình:** {avg_payment:,.0f} VNĐ")
            if scenario['rental']:
                net_avg = avg_payment - rental_income
                st.write(f"**Thực trả TB (sau thuê):** {net_avg:,.0f} VNĐ")
        
        # Biểu đồ
        st.divider()
        st.markdown("#### 📈 Biểu Đồ Chi Tiết")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Tháng'],
            y=df['Tiền gốc'],
            name='Tiền gốc',
            mode='lines',
            line=dict(color='#3B82F6', width=2),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Tháng'],
            y=df['Tiền lãi'],
            name='Tiền lãi',
            mode='lines',
            line=dict(color='#EF4444', width=2),
            fill='tozeroy'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Tháng'],
            y=df['Tổng trả'],
            name='Tổng trả',
            mode='lines',
            line=dict(color='#10B981', width=3, dash='dash')
        ))
        
        if scenario['rental']:
            net_payments = df['Tổng trả'] - rental_income
            fig.add_trace(go.Scatter(
                x=df['Tháng'],
                y=net_payments,
                name='Thực trả (sau thuê)',
                mode='lines',
                line=dict(color='#8B5CF6', width=2)
            ))
        
        fig.update_layout(
            title=f"Biểu đồ trả góp - {scenario['name']}",
            xaxis_title="Tháng",
            yaxis_title="Số tiền (VNĐ)",
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(x=0.7, y=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Bảng chi tiết (hiển thị 12 tháng đầu và 12 tháng cuối)
        st.divider()
        st.markdown("#### 📋 Lịch Trả Nợ Chi Tiết")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**12 tháng đầu tiên:**")
            display_df = df.head(12).copy()
            display_df['Dư nợ đầu kỳ'] = display_df['Dư nợ đầu kỳ'].apply(lambda x: f"{x:,.0f}")
            display_df['Tiền gốc'] = display_df['Tiền gốc'].apply(lambda x: f"{x:,.0f}")
            display_df['Tiền lãi'] = display_df['Tiền lãi'].apply(lambda x: f"{x:,.0f}")
            display_df['Tổng trả'] = display_df['Tổng trả'].apply(lambda x: f"{x:,.0f}")
            display_df['Dư nợ cuối kỳ'] = display_df['Dư nợ cuối kỳ'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**12 tháng cuối cùng:**")
            display_df = df.tail(12).copy()
            display_df['Dư nợ đầu kỳ'] = display_df['Dư nợ đầu kỳ'].apply(lambda x: f"{x:,.0f}")
            display_df['Tiền gốc'] = display_df['Tiền gốc'].apply(lambda x: f"{x:,.0f}")
            display_df['Tiền lãi'] = display_df['Tiền lãi'].apply(lambda x: f"{x:,.0f}")
            display_df['Tổng trả'] = display_df['Tổng trả'].apply(lambda x: f"{x:,.0f}")
            display_df['Dư nợ cuối kỳ'] = display_df['Dư nợ cuối kỳ'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        # Tải xuống file Excel
        if st.button(f"📥 Tải xuống lịch trả nợ đầy đủ - {scenario['name']}", key=f"download_{idx}"):
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"lich_tra_no_{scenario['name']}.csv",
                mime="text/csv",
                key=f"csv_{idx}"
            )

# So sánh các kịch bản
st.divider()
st.header("🔍 So Sánh Các Kịch Bản")

comparison_data = []
for scenario in scenarios:
    loan_amount = scenario['price'] - projected_2026
    total_months = loan_term_years * 12
    schedule = calculate_reducing_balance_loan(
        loan_amount, promo_rate, regular_rate, promo_months, total_months
    )
    df_temp = pd.DataFrame(schedule)
    
    first_payment = df_temp.iloc[0]['Tổng trả']
    last_payment = df_temp.iloc[-1]['Tổng trả']
    avg_payment = df_temp['Tổng trả'].mean()
    total_interest = df_temp['Tiền lãi'].sum()
    
    comparison_data.append({
        'Kịch bản': scenario['name'],
        'Giá nhà': scenario['price'],
        'Số tiền vay': loan_amount,
        'Trả tháng 1': first_payment,
        'Trả tháng cuối': last_payment,
        'TB/tháng': avg_payment,
        'Tổng lãi': total_interest,
        'Cho thuê': '✅' if scenario['rental'] else '❌'
    })

comparison_df = pd.DataFrame(comparison_data)

# Format số
for col in ['Giá nhà', 'Số tiền vay', 'Trả tháng 1', 'Trả tháng cuối', 'TB/tháng', 'Tổng lãi']:
    comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:,.0f}")

st.dataframe(comparison_df, hide_index=True, use_container_width=True)

# Ghi chú
st.divider()
st.info("""
### 📌 Ghi Chú:
- **Phương thức tính:** Lãi suất giảm dần (tính trên dư nợ còn lại)
- **Lãi suất ưu đãi:** Áp dụng trong giai đoạn đầu theo thông số bạn nhập
- **Lãi suất thả nổi:** Áp dụng sau khi hết thời gian ưu đãi
- **Đặc điểm:** Tháng đầu trả nhiều nhất, các tháng sau giảm dần
- **Thu nhập thuê:** Giảm gánh nặng trả góp với trường hợp cho thuê
- **Lưu ý:** Số liệu chỉ mang tính tham khảo, vui lòng liên hệ ngân hàng để có thông tin chính xác nhất
""")

st.success("💡 **Mẹo:** Điều chỉnh các thông số ở sidebar bên trái để xem kịch bản phù hợp nhất!")
