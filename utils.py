import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_progress_chart(tracker):
    """Create a bar chart showing challenge completion progress"""
    df = tracker.get_progress_data()
    
    if df.empty:
        return None
    
    fig = px.bar(
        df, 
        x='challenge', 
        y='completion',
        text=df['completion'].round(1).astype(str) + '%',
        title='Challenge Completion Progress',
        labels={'challenge': 'Challenge', 'completion': 'Completion %'},
        color='completion',
        color_continuous_scale='Viridis',
        height=400
    )
    
    fig.update_layout(
        xaxis_title="Challenge",
        yaxis_title="Completion (%)",
        yaxis=dict(range=[0, 100]),
        coloraxis_showscale=False
    )
    
    return fig

def create_xp_goal_gauge(tracker):
    """Create a gauge chart showing progress towards XP goal"""
    summary = tracker.get_summary()
    progress = summary['progress_percent']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=summary['total_xp'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "XP Progress"},
        delta={'reference': summary['xp_goal'], 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, summary['xp_goal']], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, summary['xp_goal']/3], 'color': 'red'},
                {'range': [summary['xp_goal']/3, 2*summary['xp_goal']/3], 'color': 'orange'},
                {'range': [2*summary['xp_goal']/3, summary['xp_goal']], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': summary['total_xp']
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig

def create_recent_activity_chart(tracker):
    """Create a chart showing recent XP gains over time"""
    if not tracker.history:
        return None
        
    # Extract update events from history
    updates = [h for h in tracker.history if h['action'] == 'update']
    if not updates:
        return None
        
    # Group by date and calculate total XP earned
    dates = []
    xp_values = []
    
    # Get date range for last 14 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        matching_updates = [
            u for u in updates 
            if u['timestamp'].startswith(date_str)
        ]
        
        # Simple estimation of XP earned per day
        # This is not 100% accurate without tracking daily XP
        xp_earned = 0
        if matching_updates:
            xp_earned = len(matching_updates) * 500  # Rough estimation
            
        dates.append(date_str)
        xp_values.append(xp_earned)
    
    df = pd.DataFrame({'date': dates, 'xp_earned': xp_values})
    
    fig = px.line(
        df, 
        x='date', 
        y='xp_earned',
        title='Recent XP Activity (Estimated)',
        labels={'date': 'Date', 'xp_earned': 'XP Earned'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="XP Earned",
        height=300
    )
    
    return fig
