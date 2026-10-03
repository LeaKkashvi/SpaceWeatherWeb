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
    np.random.seed(42); n=int(60+sim_kp*40)
    df=pd.DataFrame({'lat':np.random.uniform(-75,75,n),'lon':np.random.uniform(-180,180,n),'int':np.random.uniform(sim_kp*5,sim_kp*30,n)})
    fig=px.scatter_geo(df,lat='lat',lon='lon',size='int',color='int',projection='orthographic',height=600)
    fig.update_traces(marker=dict(sizemin=2,opacity=0.35))
    fig.update_geos(showland=True,landcolor='#151C28',showocean=True,oceancolor='#0B0E14',showcoastlines=True,coastlinecolor='#00F0FF',showcountries=True,countrycolor='#334155',bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',coloraxis_showscale=False)
    st.plotly_chart(fig,use_container_width=True,config={'scrollZoom':True,'responsive':True})

with tabs[2]:
    st.markdown('<h2 class="section-title">GPS PRECISION RADAR</h2>', unsafe_allow_html=True)
    st.markdown('<div class="cyber-card">Visualizing physical offset between true coordinates and GPS-indicated position.</div>',unsafe_allow_html=True)
    theta=np.linspace(0,2*np.pi,120); r=drift_val*np.ones_like(theta)
    fig=go.Figure(); fig.add_trace(go.Scatterpolar(r=[0],theta=[0],mode='markers',marker=dict(size=12,color='#00F0FF')))
    fig.add_trace(go.Scatterpolar(r=r,theta=theta,mode='lines',fill='toself',fillcolor='rgba(255,107,107,0.35)',line=dict(color='#FF6B6B',width=3)))
    for ring in [1,3,5,10,20]:
        if ring <= drift_val*1.8+5: fig.add_trace(go.Scatterpolar(r=[ring]*len(theta),theta=theta,mode='lines',line=dict(color='rgba(0,240,255,0.25)',width=1,dash='dot'),showlegend=False))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,min(30,drift_val*1.8+4)])),paper_bgcolor='#0B0E14',font=dict(color='#e2e8f0'),showlegend=False,height=550)
    st.plotly_chart(fig,use_container_width=True)

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
