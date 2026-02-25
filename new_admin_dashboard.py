def admin_dashboard():
    st.title("📈 Admin Dashboard - Healthcare Performance Rankings")
    
    # Add custom CSS for dashboard improvements
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        color: white;
        text-align: center;
    }
    .chart-title {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    .axis-label {
        font-size: 14px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    .high-percentage {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: bold;
    }
    .medium-percentage {
        background-color: #fff3cd !important;
        color: #856404 !important;
        font-weight: bold;
    }
    .low-percentage {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        font-weight: bold;
    }
    .centered-form {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get rankings and performance data
    rankings = get_woreda_rankings()
    all_data = get_performance_data()
    
    # Global KPI Section at Top
    st.markdown("### 🌍 Global Performance Indicators")
    col1, col2, col3 = st.columns(3)
    
    if not rankings.empty:
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Zone Average</h3>
                <p style="margin: 0; font-size: 18px;">No Data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Woredas Reported</h3>
                <p style="margin: 0; font-size: 18px;">0</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Total Records</h3>
                <p style="margin: 0; font-size: 18px;">0</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Calculate global metrics
        zone_avg_percentage = rankings['percentage_score'].mean()
        num_woredas_reported = len(rankings[rankings['total_score'] > 0])
        total_records = len(all_data)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Zone Average</h3>
                <p style="margin: 0; font-size: 18px;">{zone_avg_percentage:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Woredas Reported</h3>
                <p style="margin: 0; font-size: 18px;">{num_woredas_reported}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 24px;">Total Records</h3>
                <p style="margin: 0; font-size: 18px;">{total_records}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not rankings.empty:
        st.warning("📊 No performance data available. Please enter some data first!")
        return
    
    # Main Chart with Bold Labels
    st.subheader("📊 Woreda Performance Rankings")
    
    fig = px.bar(
        rankings, 
        x='percentage_score', 
        y='woreda_name',
        orientation='h',
        title='Woreda Performance Rankings (%)',
        color='percentage_score',
        color_continuous_scale=px.colors.sequential.Viridis,
        height=600
    )
    
    # Update chart layout for bold labels
    fig.update_layout(
        font=dict(size=14, family="Arial", color="black"),
        xaxis_title_font=dict(size=16, family="Arial", color="black"),
        yaxis_title_font=dict(size=16, family="Arial", color="black"),
        title_font=dict(size=20, family="Arial", color="black"),
        xaxis=dict(title='Performance Score (%)', tickfont=dict(size=12, family="Arial")),
        yaxis=dict(title='Woreda Name', tickfont=dict(size=12, family="Arial"))
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ranking Table with Conditional Formatting
    st.subheader("📋 Detailed Ranking Table")
    
    # Create ranking table with conditional formatting
    ranking_data = []
    for rank, (index, row) in enumerate(rankings.itertuples(), 1):
        percentage = row.percentage_score
        
        # Apply conditional formatting
        if percentage >= 90:
            percentage_class = "high-percentage"
            percentage_display = f"**{percentage:.1f}%** ✅"
        elif percentage >= 50:
            percentage_class = "medium-percentage"
            percentage_display = f"**{percentage:.1f}%** ⚠️"
        else:
            percentage_class = "low-percentage"
            percentage_display = f"**{percentage:.1f}%** ❌"
        
        ranking_data.append({
            'Rank': rank,
            'Woreda Name': row.woreda_name,
            'Total Score (Out of 110)': f"{row.total_score:.1f}",
            'Final Percentage (%)': percentage_display
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    
    # Apply custom CSS for conditional formatting
    st.markdown("""
    <style>
    .dataframe td {
        font-size: 14px !important;
        font-weight: bold !important;
    }
    .dataframe th {
        font-size: 16px !important;
        font-weight: bold !important;
        background-color: #1f77b4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    # Departmental Stacked Bar Chart
    st.subheader("🏥 Departmental Contribution Analysis")
    
    # Prepare data for stacked bar chart
    dept_columns = [
        'medical_service', 'rmh', 'pharmacy_logistic', 'ultrasound', 'apts', 'community_pharmacy', 'dm_test',
        'epi', 'child_health', 'tb_leprosy', 'phem', 'cbhi', 'finance', 'plan', 'wt',
        'full_emr', 'epi_modernization', 'zero_dose', 'multi_sectoral', 'cash_program', 'hygiene_sanitation'
    ]
    
    dept_labels = {
        'medical_service': 'Medical Service', 'rmh': 'RMH', 'pharmacy_logistic': 'Pharmacy & Logistic',
        'ultrasound': 'Ultrasound', 'apts': 'APTS', 'community_pharmacy': 'Community Pharmacy',
        'dm_test': 'DM Test', 'epi': 'EPI', 'child_health': 'Child Health',
        'tb_leprosy': 'TB & Leprosy', 'phem': 'PHEM', 'cbhi': 'CBHI',
        'finance': 'Finance', 'plan': 'Plan', 'wt': 'WT', 'full_emr': 'Full EMR',
        'epi_modernization': 'EPI Modernization', 'zero_dose': 'Zero Dose',
        'multi_sectoral': 'Multi-Sectoral', 'cash_program': 'Cash Program', 'hygiene_sanitation': 'Hygiene & Sanitation'
    }
    
    # Aggregate data by woreda for stacked chart
    woreda_dept_data = []
    for woreda in rankings['woreda_name'].unique():
        woreda_data = all_data[all_data['woreda_name'] == woreda]
        
        dept_contributions = {}
        for dept_col in dept_columns:
            if dept_col in woreda_data.columns:
                total = woreda_data[dept_col].sum()
                if total > 0:
                    dept_contributions[dept_labels.get(dept_col, dept_col)] = total
        
        if dept_contributions:
            dept_contributions['Woreda'] = woreda
            woreda_dept_data.append(dept_contributions)
    
    if woreda_dept_data:
        dept_df = pd.DataFrame(woreda_dept_data)
        dept_df = dept_df.fillna(0)
        
        # Create stacked bar chart
        fig_stacked = px.bar(
            dept_df,
            x='Woreda',
            y=[col for col in dept_columns if col in dept_labels.values()],
            title="Departmental Contribution to Total Score (Out of 110)",
            labels={
                col: dept_labels.get(col, col) 
                for col in dept_columns 
                if col in dept_labels.values()
            },
            barmode='stack',
            height=500
        )
        
        # Update layout for better visibility
        fig_stacked.update_layout(
            font=dict(size=12, family="Arial"),
            xaxis_title_font=dict(size=14, family="Arial"),
            yaxis_title_font=dict(size=14, family="Arial"),
            title_font=dict(size=16, family="Arial"),
            xaxis=dict(tickangle=45),
            yaxis=dict(title='Score Contribution')
        )
        
        st.plotly_chart(fig_stacked, use_container_width=True)
    
    # Detailed Woreda Analysis
    st.subheader("🔍 Detailed Woreda Analysis")
    
    selected_woreda = st.selectbox(
        "Select Woreda for Detailed Analysis:",
        options=rankings['woreda_name'].tolist(),
        key="detailed_woreda_analysis"
    )
    
    if selected_woreda:
        woreda_detailed_data = all_data[all_data['woreda_name'] == selected_woreda]
        
        if not woreda_detailed_data.empty:
            st.warning(f"No detailed data found for {selected_woreda}")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**📊 Performance Breakdown for {selected_woreda}:**")
                
                # Calculate departmental breakdown
                dept_breakdown = {}
                for dept_col in dept_columns:
                    if dept_col in woreda_detailed_data.columns:
                        total = woreda_detailed_data[dept_col].sum()
                        if total > 0:
                            dept_breakdown[dept_labels.get(dept_col, dept_col)] = total
                
                if dept_breakdown:
                    breakdown_df = pd.DataFrame(list(dept_breakdown.items()), columns=['Department', 'Score'])
                    breakdown_df['Percentage'] = (breakdown_df['Score'] / breakdown_df['Score'].sum() * 100).round(1)
                    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            
            with col2:
                # Radar chart for selected woreda
                dept_scores = {}
                for dept_col in dept_columns:
                    if dept_col in woreda_detailed_data.columns:
                        total = woreda_detailed_data[dept_col].sum()
                        if total > 0:
                            dept_scores[dept_labels.get(dept_col, dept_col)] = total
                
                if dept_scores:
                    fig_radar = go.Figure()
                    
                    categories = list(dept_scores.keys())
                    values = list(dept_scores.values())
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=selected_woreda,
                        line_color='rgb(31, 119, 180)',
                        fillcolor='rgba(31, 119, 180, 0.25)'
                    ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, max(values) * 1.1] if values else [0, 10]
                            )
                        ),
                        title=dict(text=f'{selected_woreda} - Departmental Performance', font=dict(size=16)),
                        font=dict(size=12)
                    )
                    
                    st.plotly_chart(fig_radar, use_container_width=True)
