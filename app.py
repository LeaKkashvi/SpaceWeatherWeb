import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='HelioGuard Mission Control', page_icon=':satellite:', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Orbitron:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
html, body, .stApp { background: radial-gradient(circle at 50% 20%, #080D1A 0%, #03050C 100%); font-family: 'Inter', sans-serif; color: #E2E8F0; }
.hud-zone { background: linear-gradient(135deg, rgba(15,23,42,0.85) 0%, rgba(11,28,48,0.90) 100%); backdrop-filter: blur(16px); border-bottom: 2px solid #00F0FF; box-shadow: 0 10px 30px rgba(0,240,255,0.25); padding: 12px 16px 0 16px; margin: -4px -16px 12px -16px; position: relative; }
.laser-underline { position: absolute; left: 0; bottom: -2px; width: 100%; height: 3px; background: radial-gradient(ellipse at center, rgba(0,240,255,1) 0%, rgba(0,240,255,0.4) 40%, rgba(0,240,255,0) 100%); filter: blur(1px); animation: pulse-laser 2.4s ease-in-out infinite; }
@keyframes pulse-laser { 0%{opacity:0.6} 50%{opacity:1} 100%{opacity:0.6} }
.hud-bar { display:flex; flex-wrap:wrap; gap:14px; justify-content:space-between; padding:8px 0 10px 0; }
.hud-item { font-family:'Share Tech Mono', monospace; font-size:13px; color:#E2E8F0; }
.hud-item .val { color:#00F0FF; text-shadow:0 0 12px rgba(0,240,255,0.7); }
.pulse-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#22c55e; box-shadow:0 0 12px #22c55e; animation:pulse 1.6s infinite; }
@keyframes pulse { 0%{opacity:1} 50%{opacity:0.3} 100%{opacity:1} }
.cmd-title { font-family:'Orbitron', sans-serif; font-size:24px; color:#00F0FF; text-shadow:0 0 10px rgba(0,240,255,0.6), 0 0 20px rgba(0,240,255,0.4); letter-spacing:2px; margin:6px 0 4px 0; }
.cmd-sub { font-family:'Share Tech Mono', monospace; color:#94a3b8; font-size:12px; margin-top:-4px; }
.cyber-card { border:1px solid #00F0FF33; border-radius:10px; padding:14px; background:rgba(15,23,42,0.7); box-shadow:inset 0 1px 0 rgba(255,255,255,0.05), 0 0 25px rgba(0,240,255,0.08); }
.cyber-metric .num { font-family:'Share Tech Mono', monospace; font-size:28px; color:#00F0FF; text-shadow:0 0 12px rgba(0,240,255,0.8); }
.section-title { font-family:'Orbitron', sans-serif; color:#00F0FF; text-shadow:0 0 10px rgba(0,240,255,0.6); }
.workzone { background: radial-gradient(circle at 50% 20%, #080D1A 0%, #03050C 100%); padding: 4px 16px 24px 16px; margin: 0 -16px; background-image: linear-gradient(rgba(0,240,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.03) 1px, transparent 1px); background-size: 40px 40px; }
div.stTabs button[role='tab'] { font-family:'Orbitron', sans-serif; color:rgba(255,255,255,0.6); border:1px solid #1e293b; background:rgba(15,23,42,0.5); margin-right:6px; border-radius:8px 8px 0 0; }
div.stTabs button[role='tab'][aria-selected='true'] { color:#00F0FF; border:1px solid #00F0FF; background:rgba(0,240,255,0.12); text-shadow:0 0 10px rgba(0,240,255,0.7); box-shadow:inset 0 -3px 0 #00F0FF; }
div.stTabs div[role='tablist'] { border-bottom:1px solid #1e293b; }
.glow-alert { border-left:4px solid #f59e0b; padding:12px; border-radius:8px; background:rgba(245,158,11,0.12); box-shadow:0 0 20px rgba(245,158,11,0.25); }
</style>''', unsafe_allow_html=True)

# HUD zone
st.markdown('''<div class="hud-zone">
  <div class="cmd-title">HELiOGUARD MISSION CONTROL</div>
  <div class="cmd-sub">REAL-TIME GEOSPACE TELEMETRY & AUTONOMOUS NAVIGATION RISK ENGINE</div>
  <div class="hud-bar">
    <div class="hud-item"><span class="pulse-dot"></span> LIVE GEOSPACE SURVEY ACTIVE</div>
    <div class="hud-item">GNSS: <span class="val">32 / 32 GNSS LOCKED</span></div>
    <div class="hud-item">SOLAR WIND: <span class="val">452 km/s (NORMAL)</span></div>
    <div class="hud-item">IONOSPHERIC TEC: <span class="val">18.4 TECU</span></div>
    <div class="hud-item">GEOMAGNETIC: <span class="val">G1 MINOR WATCH</span></div>
  </div>
  <div class="laser-underline"></div>
</div>''', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<h2 style="font-family:Orbitron,sans-serif;color:#00F0FF;text-shadow:0 0 10px rgba(0,240,255,0.4);">HelioGuard Controls</h2>', unsafe_allow_html=True)
    sector = st.selectbox('Select Sector', ['Drone Pilot / Surveyor', 'Precision Agriculture', 'Maritime & Port Ops', 'Logistics & Fleet', 'Emergency Services & Ambulances', 'Autonomous Aviation / Drones'])
    sim_kp = st.slider('Storm Intensity (Kp)', 0.0, 9.0, 2.3, 0.1)

drift_val = round(0.2 + sim_kp * 0.45, 2)
if sim_kp < 4.0: risk_level = 'LOW'
elif sim_kp < 7.0: risk_level = 'MEDIUM'
else: risk_level = 'HIGH'

# Executive metrics under HUD
c1,c2,c3 = st.columns(3)
c1.markdown(f'<div class="cyber-card cyber-metric"><h3>RISK LEVEL</h3><div class="num">{risk_level}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="cyber-card cyber-metric"><h3>ESTIMATED DRIFT</h3><div class="num">+/-{drift_val}m</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="cyber-card cyber-metric"><h3>PRIMARY SECTOR</h3><div class="num" style="font-size:20px;color:#FFB000;text-shadow:0 0 12px rgba(255,176,0,0.6)">{sector}</div></div>', unsafe_allow_html=True)

directives = {
  'Drone Pilot / Surveyor': 'Maintain line-of-sight and verify RTK corrections.',
  'Precision Agriculture': 'Monitor automated steering; prepare manual override.',
  'Maritime & Port Ops': 'Verify critical navigation references.',
  'Logistics & Fleet': 'Increase position verification intervals.',
  'Emergency Services & Ambulances': 'WARNING: High GPS drift may misguide automated dispatching or lane-keeping systems.',
  'Autonomous Aviation / Drones': 'WARNING: Drift can degrade precision landing and obstacle avoidance.',
}
st.markdown(f'<div class="glow-alert"><b>OPERATIONAL DIRECTIVE</b><br>{sector}: {directives.get(sector,"Monitor and assess operational impact.")}</div>', unsafe_allow_html=True)
st.markdown('<br>',unsafe_allow_html=True)

# Tabs in workzone
tabs = st.tabs(['Mission Overview','3D Ionosphere Globe','GPS Precision Radar','Storm Simulator','Industry Matrix'])

# wrap content
st.markdown('<div class="workzone">', unsafe_allow_html=True)
with tabs[0]:
    st.markdown('<h2 class="section-title">GEOMAGNETIC STORM ANATOMY</h2>', unsafe_allow_html=True)
    st.markdown('<div class="cyber-card">1. Solar Ejection  ->  2. Ionospheric Ionization  ->  3. Satellite Signal Delay  ->  4. Ground Positioning Drift</div>', unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<div class="cyber-card">GPS drift occurs as ionospheric delays propagate through navigation signals. These errors directly impact precision operations, making real-time assessment critical for mission safety.</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<h2 class="section-title">3D IONOSPHERE GLOBE</h2>', unsafe_allow_html=True)
    np.random.seed(42)
    stations=[
        ('Western USA / Colorado',40.03,-105.28),
        ('Alaska / USA',64.84,-147.72),
        ('Northeastern USA / Massachusetts',42.62,-71.49),
        ('Central Canada / Ontario',45.42,-75.70),
        ('Central Mexico / Mexico City',19.43,-99.13),
        ('Central Chile / Santiago',-33.45,-70.67),
        ('Southeastern Brazil / Sao Paulo',-23.55,-46.63),
        ('Eastern Argentina / Buenos Aires',-34.60,-58.38),
        ('Western Peru / Lima',-12.05,-77.04),
        ('Northern Colombia / Bogota',4.71,-74.07),
        ('Northern Scandinavia / Sweden',67.86,20.23),
        ('Arctic Norway / Tromso',69.65,18.96),
        ('Western Europe / United Kingdom',51.51,-0.13),
        ('Central Europe / Germany',52.52,13.40),
        ('Southern Europe / Italy',41.90,12.50),
        ('Iberian Peninsula / Spain',40.42,-3.70),
        ('Northern Africa / Egypt',30.04,31.24),
        ('Western Africa / Nigeria',6.52,3.38),
        ('Eastern Africa / Kenya',-1.29,36.82),
        ('Southern Africa / South Africa',-34.42,19.22),
        ('Western Africa / Senegal',14.72,-17.47),
        ('Eastern Asia / Japan',35.68,139.69),
        ('South Asia / India',28.61,77.21),
        ('Eastern Asia / China',39.90,116.41),
        ('Southeastern Asia / Thailand',13.76,100.50),
        ('Middle East / United Arab Emirates',25.20,55.27),
        ('Southeastern Asia / Singapore',1.35,103.82),
        ('Eastern Asia / South Korea',37.57,126.98),
        ('Central Asia / Kazakhstan',43.24,76.89),
        ('Southeastern Australia / Sydney',-33.87,151.21),
        ('Western Australia / Perth',-31.95,115.86),
        ('New Zealand / North Island',-36.85,174.76),
        ('South Australia / Adelaide',-34.93,138.60),
        ('Sub-Antarctic / Kerguelen Islands',-49.35,69.50),
        ('Antarctica / McMurdo Station',-77.85,166.67),
        ('Antarctica / Casey Station',-66.28,110.53),
    ]
    n=len(stations)
    st_lat=np.array([s[1] for s in stations]); st_lon=np.array([s[2] for s in stations])
    tec=np.random.uniform(4+sim_kp*2,12+sim_kp*25,n)
    kp_pts=np.clip(sim_kp+np.random.uniform(-0.6,0.6,n),0,9)
    def gps_status(k):
        if k < 4: return 'Normal - Safe for Precision Farming'
        if k < 7: return 'Slightly Delayed - Watch for GPS Drift'
        return 'Degraded - High Risk of GPS Error'
    def solar_effect(k):
        if k < 4: return 'Quiet Sun - No Disruptions'
        if k < 7: return 'Active Solar Wind - Use Caution'
        return 'Geomagnetic Storm - Expect Signal Loss'
    def risk_color(k):
        if k < 4: return '#22C55E'
        if k < 7: return '#FFB000'
        return '#EF4444'
    def risk_glow(k):
        if k < 4: return 'rgba(34,197,94,0.16)'
        if k < 7: return 'rgba(255,176,0,0.16)'
        return 'rgba(239,68,68,0.20)'
    node_colors=[risk_color(float(k)) for k in kp_pts]
    glow_colors=[risk_glow(float(k)) for k in kp_pts]
    custom=[(s[0],gps_status(float(kp_pts[i])),solar_effect(float(kp_pts[i]))) for i,s in enumerate(stations)]
    fig=go.Figure()
    fig.add_trace(go.Scattergeo(lat=st_lat,lon=st_lon,mode='markers',
        marker=dict(size=tec/1.4+10,color=glow_colors,line=dict(width=0)),hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scattergeo(lat=st_lat,lon=st_lon,mode='markers',
        marker=dict(size=tec/3+5,color=node_colors,opacity=0.95,line=dict(width=1,color='#EAFEFF')),
        customdata=custom,
        hovertemplate=('<b>%{customdata[0]}</b><br>GPS Signal Status: %{customdata[1]}<br>'
            'Solar Activity Effect: %{customdata[2]}<extra></extra>'),showlegend=False))
    fig.update_geos(projection=dict(type='orthographic'),
        showland=True,landcolor='#1E293B',
        showocean=True,oceancolor='#0F172A',
        showcoastlines=True,coastlinecolor='#00F0FF',coastlinewidth=1,
        showcountries=True,countrycolor='#00F0FF',countrywidth=1.5,
        showframe=False,showlakes=True,lakecolor='#0F172A',bgcolor='#070B19',
        lataxis=dict(showgrid=True,gridcolor='rgba(0,240,255,0.15)',gridwidth=0.5),
        lonaxis=dict(showgrid=True,gridcolor='rgba(0,240,255,0.15)',gridwidth=0.5))
    fig.frames=[go.Frame(layout=dict(geo=dict(projection=dict(type='orthographic',rotation=dict(lon=i,lat=15))))) for i in range(0,360,5)]
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor='#070B19',plot_bgcolor='#070B19',
        showlegend=False,height=600,
        hoverlabel=dict(bgcolor='#070B19',bordercolor='#00F0FF',font=dict(color='#00F0FF',family='Share Tech Mono')),
        updatemenus=[dict(type='buttons',showactive=False,direction='right',bgcolor='#0F172A',
            bordercolor='#00F0FF',font=dict(color='#00F0FF',family='Share Tech Mono'),
            x=0.01,y=1.09,xanchor='left',yanchor='top',
            buttons=[dict(label='\u25B6 ROTATE',method='animate',
                    args=[None,dict(frame=dict(duration=120,redraw=True),fromcurrent=True,transition=dict(duration=0))]),
                dict(label='\u275A\u275A HOLD',method='animate',
                    args=[[None],dict(frame=dict(duration=0,redraw=False),mode='immediate')])])])
    st.plotly_chart(fig,use_container_width=True,config={'scrollZoom':True,'responsive':True,'displayModeBar':True})

with tabs[2]:
    st.markdown('<h2 class="section-title">GPS PRECISION RADAR</h2>', unsafe_allow_html=True)
    st.markdown('<div class="cyber-card">TACTICAL NAVIGATION HUD \u2014 true-position anchor vs. real-time GPS drift envelope.</div>',unsafe_allow_html=True)
    theta_full=np.linspace(0,2*np.pi,240); theta_deg=np.degrees(theta_full)
    status_color='#22C55E' if risk_level=='LOW' else ('#FFB000' if risk_level=='MEDIUM' else '#EF4444')
    jitter='NOMINAL' if risk_level=='LOW' else ('ELEVATED' if risk_level=='MEDIUM' else 'SEVERE')
    drift_bearing=45
    fig=go.Figure()
    for scale,op in [(1.0,0.30),(1.7,0.16),(2.5,0.07)]:
        fig.add_trace(go.Scatterpolar(r=(drift_val*scale)*np.ones_like(theta_full),theta=theta_deg,mode='lines',
            fill='toself',fillcolor=f'rgba(255,176,0,{op})',line=dict(color='rgba(255,176,0,0.45)',width=1),
            hoverinfo='skip',showlegend=False))
    for rr,op,w in [(1,0.10,1),(5,0.18,1),(10,0.28,1.2),(20,0.42,1.5)]:
        fig.add_trace(go.Scatterpolar(r=[rr]*len(theta_deg),theta=theta_deg,mode='lines',
            line=dict(color=f'rgba(0,240,255,{op})',width=w),hoverinfo='skip',showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[rr],theta=[135],mode='text',text=[f'\u00B1{rr}m'],
            textfont=dict(color=f'rgba(0,240,255,{min(op+0.25,0.9)})',size=10,family='Share Tech Mono'),
            hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[21.8]*4,theta=[90,0,270,180],mode='text',text=['N','E','S','W'],
        textfont=dict(color='#00F0FF',size=17,family='Share Tech Mono'),hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[0,drift_val],theta=[0,drift_bearing],mode='lines',
        line=dict(color='#FFB000',width=2,dash='dash'),hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[drift_val],theta=[drift_bearing],mode='markers+text',
        marker=dict(symbol='x',size=15,color='#FFB000',line=dict(color='#FFB000',width=2)),
        text=[f'  GPS FIX \u00B1{drift_val:.2f}m'],textposition='top center',
        textfont=dict(color='#FFB000',size=11,family='Share Tech Mono'),
        hovertemplate=f'CURRENT GPS FIX<br>OFFSET: \u00B1{drift_val:.2f} m<extra></extra>',showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[0],theta=[0],mode='markers',
        marker=dict(symbol='star',size=24,color='#FFFFFF',line=dict(color='#00F0FF',width=2)),
        hovertemplate='TRUE POSITION<br>ANCHOR LOCKED<extra></extra>',showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[0],theta=[0],mode='markers',
        marker=dict(symbol='circle',size=8,color='#00FF9C'),hoverinfo='skip',showlegend=False))
    fig.add_annotation(x=0.02,y=0.98,xref='paper',yref='paper',xanchor='left',yanchor='top',showarrow=False,
        align='left',bordercolor=status_color,borderwidth=1.5,borderpad=8,bgcolor='rgba(7,11,25,0.85)',
        font=dict(color=status_color,size=12,family='Share Tech Mono'),
        text=(f'<b>\u25C6 NAV STATUS: {risk_level}</b><br>POSITION ERROR: \u00B1{drift_val:.2f} m<br>'
              f'IONO JITTER: {jitter}<br>Kp INDEX: {sim_kp:.1f}  |  SATS: 32'))
    fig.update_layout(
        polar=dict(bgcolor='#0F172A',
            radialaxis=dict(range=[0,22.5],showline=False,showticklabels=True,ticks='',
                tickfont=dict(color='rgba(0,240,255,0.45)',size=9,family='Share Tech Mono'),
                gridcolor='rgba(0,240,255,0.15)',gridwidth=1,tickvals=[0,5,10,15,20]),
            angularaxis=dict(showline=False,gridcolor='rgba(0,240,255,0.15)',gridwidth=1,
                tickfont=dict(color='rgba(0,240,255,0.45)',size=9,family='Share Tech Mono'))),
        paper_bgcolor='#070B19',plot_bgcolor='#070B19',font=dict(color='#E2E8F0'),
        showlegend=False,height=600,margin=dict(l=40,r=40,t=70,b=40))
    st.plotly_chart(fig,use_container_width=True,config={'scrollZoom':True,'responsive':True})

with tabs[3]:
    st.markdown('<h2 class="section-title">STORM SIMULATOR</h2>', unsafe_allow_html=True)
    kp_s=st.slider('Kp Index (0.0 - 9.0)',0.0,9.0,float(sim_kp),0.1)
    d2=round(0.2+kp_s*0.45,2)
    if kp_s<4: r2='LOW'
    elif kp_s<7: r2='MEDIUM'
    else: r2='HIGH'
    dfc=pd.DataFrame({'Scenario':['Baseline (Kp=2.0)','Simulated'],'Kp':[2.0,kp_s],'Drift':[f'+/-{round(0.2+2.0*0.45,2)}m',f'+/-{d2}m'],'Risk':['LOW',r2]})
    dfc=pd.DataFrame({'Scenario':['Baseline (Kp=2.0)','Simulated'],'Kp':[2.0,kp_s],'Drift':[f'+/-{round(0.2+2.0*0.45,2)}m',f'+/-{d2}m'],'Risk':['LOW',r2]})
    st.dataframe(dfc,hide_index=True,use_container_width=True)

with tabs[4]:
    st.markdown('<h2 class="section-title">INDUSTRY SAFETY MATRIX</h2>', unsafe_allow_html=True)
    sectors=[('Drone Pilot / Surveyor',0.5),('Precision Agriculture',2.0),('Maritime & Port Ops',5.0),('Logistics & Fleet',10.0),('Emergency Services & Ambulances',2.5),('Autonomous Aviation / Drones',0.8)]
    danger_count=0
    for name,tol in sectors:
        if drift_val > tol*1.5: danger_count+=1
    if danger_count>0:
        st.markdown(f'<div style="background: rgba(239,68,68,0.12); border-left: 5px solid #EF4444; padding: 14px; border-radius: 4px; font-family: Orbitron, sans-serif; color:#FFFFFF; text-shadow:0 0 10px rgba(239,68,68,0.6);">WARNING: GPS DRIFT EXCEEDS SAFETY TOLERANCE FOR {danger_count} OPERATIONAL SECTORS</div>', unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    for name,tol in sectors:
        if drift_val<=tol: status='Safe'; badge='<span style="background:rgba(16,185,129,0.15); color:#10B981; border:1px solid #10B981; padding:4px 12px; border-radius:20px; font-weight:bold; text-shadow:0 0 8px rgba(16,185,129,0.4);">SAFE</span>'; barc='#10B981'
        elif drift_val<=tol*1.5: status='Caution'; badge='<span style="background:rgba(245,158,11,0.15); color:#F59E0B; border:1px solid #F59E0B; padding:4px 12px; border-radius:20px; font-weight:bold; text-shadow:0 0 8px rgba(245,158,11,0.4);">CAUTION</span>'; barc='#F59E0B'
        else: status='Danger'; badge='<span style="background:rgba(239,68,68,0.2); color:#EF4444; border:1px solid #EF4444; padding:4px 12px; border-radius:20px; font-weight:bold; animation:pulse 1.5s infinite; text-shadow:0 0 8px rgba(239,68,68,0.6);">DANGER</span>'; barc='#EF4444'
        pct = min(100, (drift_val / (tol*2.0)) * 100)
        st.markdown(f'<div class="cyber-card"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;"><b>{name}</b>{badge}</div><div style="font-size:13px; color:#94a3b8;">Max Tolerance: {tol}m | Current Drift: {round(float(drift_val),2)}m</div><div style="background:#0f172a; border-radius:4px; height:8px; margin-top:10px; border:1px solid #1e293b;"><div style="width:{pct:.1f}%; background:{barc}; height:6px; border-radius:3px;"></div></div></div><br>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
