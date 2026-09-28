"""
GraphGuardians - Multi-Page Enterprise Agentic Fraud Ring Detection & Countermeasure Engine

Full Agentic Pipeline:
- Step 0: Real SQLite Officer Authentication (3D Ring Portal)
- Page 1: Ingestion & Dataset Setup (Custom CSV file uploader + Schema detection + Data summary preview)
- Page 2: Dual 3D/2D Graph Topology + Multi-Agent Reasoning + Dynamic Account Freeze Controls
  - Top KPI Strip: Total Amount Scammed & Accounts To Freeze (Computed from user input dataset)
  - Clear Dual Graph Views: 3D Fiber-Optic Wire Connections + 2D High-Contrast Interactive Node-Edge Graph
  - Agent Actions Panel: Target accounts freeze controls, human override audit trail, FinCEN SAR downloads, CSV export
- Page 3: Team Architecture & SQLite Audit Trail Logs
"""

import os
import re
import time
import json
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import importlib

# Backend Modules
from data_utils import load_transactions
from graph_builder import build_transaction_graph, detect_transaction_columns
from explainability import get_account_hover_summary
import agents
import countermeasures
import db
importlib.reload(db)  # Ensure fresh module reload

# ---------------------------------------------------------------------------
# STREAMLIT PAGE CONFIG & HIGH-END ENTERPRISE STYLES
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="GraphGuardians - Enterprise Fraud Intelligence",
    page_icon="https://svgsilh.com/svg/2793139.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    .stApp {
        background-color: #070a13;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* STREAMLIT FILE UPLOADER BUTTON FIX - REMOVE OVERLAPPING ICON TEXT */
    [data-testid="stFileUploader"] button {
        font-family: 'Share Tech Mono', monospace !important;
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="stFileUploader"] button:hover {
        border-color: #a855f7 !important;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.4) !important;
    }
    /* Hide broken icon text node 'upload' */
    [data-testid="stFileUploader"] button span:first-child,
    [data-testid="stFileUploader"] button small:first-child {
        font-size: 0px !important;
        width: 0px !important;
        height: 0px !important;
        opacity: 0 !important;
        visibility: hidden !important;
        display: none !important;
    }
    /* Ensure label text is clean, visible, and styled */
    [data-testid="stFileUploader"] button span:last-child {
        font-size: 0.88rem !important;
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        visibility: visible !important;
        display: inline-block !important;
    }

    /* GLOBAL HIGH-TECH TYPOGRAPHY & GLOW SYSTEM ACROSS ALL PAGES */
    h1, h2, h3, h4, h5, h6,
    .stButton > button,
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stRadio label,
    .bank-title,
    .bank-badge,
    .login-portal-title,
    .login-portal-sub,
    .step-number,
    .step-title,
    .tva-kpi-label,
    .tva-kpi-value,
    .tier-badge,
    .db-badge {
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 0.6px !important;
    }

    /* Ambient Futuristic Glow on All Headings Across Entire Website */
    h1, h2, h3, h4, .bank-title, .login-portal-title {
        text-shadow: 0 0 20px rgba(168, 85, 247, 0.45) !important;
    }

    /* Unified Sleek Inputs Across All Pages */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stNumberInput input {
        font-family: 'Share Tech Mono', monospace !important;
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.5) !important;
    }

    /* Unified Sleek Buttons Across All Pages */
    .stButton > button {
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.45) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 30px rgba(168, 85, 247, 0.7) !important;
    }

    .bank-header {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 12px;
        padding: 18px 26px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.45), 0 0 20px rgba(245, 158, 11, 0.12);
    }
    .bank-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #f59e0b;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .bank-badge {
        background-color: #1e293b;
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid #0284c7;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .login-fullscreen-wrapper {
        position: relative !important;
        z-index: 20 !important;
        max-width: 480px !important;
        margin: 40px auto 0 auto !important;
        text-align: center;
    }
    .login-portal-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #a855f7;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
        text-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
        font-family: 'Share Tech Mono', monospace !important;
    }
    .login-portal-sub {
        font-size: 0.82rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Share Tech Mono', monospace !important;
    }

    /* BORDER GLOW ANIMATED EFFECT FOR LOGIN PROFILE CARD */
    @keyframes borderGlowSweep {
        0% {
            box-shadow: 
                0 0 20px rgba(192, 132, 252, 0.5),
                0 0 40px rgba(244, 114, 182, 0.3),
                0 0 60px rgba(56, 189, 248, 0.2),
                inset 0 0 15px rgba(192, 132, 252, 0.15),
                0 20px 50px rgba(0, 0, 0, 0.9);
        }
        50% {
            box-shadow: 
                0 0 28px rgba(244, 114, 182, 0.6),
                0 0 50px rgba(56, 189, 248, 0.35),
                0 0 70px rgba(192, 132, 252, 0.25),
                inset 0 0 20px rgba(244, 114, 182, 0.2),
                0 20px 50px rgba(0, 0, 0, 0.9);
        }
        100% {
            box-shadow: 
                0 0 20px rgba(56, 189, 248, 0.5),
                0 0 40px rgba(192, 132, 252, 0.3),
                0 0 60px rgba(244, 114, 182, 0.2),
                inset 0 0 15px rgba(56, 189, 248, 0.15),
                0 20px 50px rgba(0, 0, 0, 0.9);
        }
    }

    div[data-testid="stForm"] {
        position: relative !important;
        isolation: isolate !important;
        border-radius: 28px !important;
        background: #120F17 !important;
        border: 2px solid transparent !important;
        background-image: linear-gradient(#120F17, #120F17), linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #38bdf8 100%) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        animation: borderGlowSweep 4s infinite alternate ease-in-out !important;
        padding: 32px 30px !important;
        max-width: 440px !important;
        margin: 30px auto 30px auto !important;
        box-sizing: border-box !important;
        transition: transform 0.3s ease !important;
    }

    div[data-testid="stForm"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 
            0 0 35px rgba(192, 132, 252, 0.7),
            0 0 65px rgba(244, 114, 182, 0.5),
            0 0 95px rgba(56, 189, 248, 0.4),
            inset 0 0 25px rgba(192, 132, 252, 0.25),
            0 25px 60px rgba(0, 0, 0, 0.95) !important;
    }
    div[data-testid="stForm"] > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stForm"] [data-testid="stVerticalBlock"] {
        gap: 12px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stForm"] .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stForm"] h4 {
        margin: 0 0 14px 0 !important;
        padding: 0 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-align: center !important;
        text-shadow: 0 0 15px rgba(168, 85, 247, 0.6) !important;
        font-size: 1.3rem !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-testid="stForm"] label p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        margin-bottom: 4px !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-testid="stForm"] input {
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-testid="stForm"] input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.5) !important;
    }
    div[data-testid="stForm"] button[type="submit"] {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.45) !important;
        border-radius: 10px !important;
        margin-top: 6px !important;
        transition: all 0.3s ease !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-testid="stForm"] button[type="submit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 30px rgba(168, 85, 247, 0.7) !important;
    }

    .guide-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
        transition: border-color 0.3s ease;
    }
    .guide-card:hover {
        border-color: #f59e0b;
    }
    .step-number {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.25rem;
        font-weight: 700;
        color: #f59e0b;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    .step-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 6px;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .step-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.55;
    }

    .tva-kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 22px;
    }
    .tva-kpi-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .tva-kpi-label {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .tva-kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #f59e0b;
        margin: 0;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .tva-kpi-value.danger { color: #f43f5e; }

    .tier-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.78rem;
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 0.5px;
    }
    .tier-CRITICAL { background: #f43f5e; color: #ffffff; }
    .tier-HIGH { background: #f97316; color: #ffffff; }
    .tier-MEDIUM { background: #eab308; color: #0f172a; }
    .tier-LOW { background: #10b981; color: #ffffff; }

    .agent-action-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .db-badge {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid #059669;
        padding: 6px 14px;
        border-radius: 6px;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.82rem;
        margin-bottom: 18px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# 3D MAGIC RINGS SHADER COMPONENT FOR LOGIN PORTAL
# ---------------------------------------------------------------------------
def render_magic_rings_html(color="#A855F7", color_two="#3B82F6", height=500):
    """Renders high-performance full-screen WebGL GLSL magic rings 3D concentric shader animation."""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body, html {{ margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; background: transparent; }}
        #canvas-container {{ width: 100vw; height: 100vh; position: fixed; top: 0; left: 0; }}
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
      <div id="canvas-container"></div>
      <script>
        const vertexShader = `
          void main() {{
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }}
        `;

        const fragmentShader = `
          precision highp float;

          uniform float uTime, uAttenuation, uLineThickness;
          uniform float uBaseRadius, uRadiusStep, uScaleRate;
          uniform float uOpacity, uNoiseAmount, uRotation, uRingGap;
          uniform float uFadeIn, uFadeOut;
          uniform float uMouseInfluence, uHoverAmount, uHoverScale, uParallax, uBurst;
          uniform float uCoverageAlpha;
          uniform vec2 uResolution, uMouse;
          uniform vec3 uColor, uColorTwo;
          uniform int uRingCount;

          const float HP = 1.5707963;
          const float CYCLE = 3.8;

          float fade(float t) {{
            return t < uFadeIn ? smoothstep(0.0, uFadeIn, t) : 1.0 - smoothstep(uFadeOut, CYCLE - 0.2, t);
          }}

          float ring(vec2 p, float ri, float cut, float t0, float px) {{
            float t = mod(uTime + t0, CYCLE);
            float r = ri + t / CYCLE * uScaleRate;
            float d = abs(length(p) - r);
            float a = atan(abs(p.y), abs(p.x)) / HP;
            float th = max(1.0 - a, 0.5) * px * uLineThickness;
            float h = (1.0 - smoothstep(th, th * 1.5, d)) + 1.0;
            d += pow(cut * a, 3.0) * r;
            return h * exp(-uAttenuation * d) * fade(t);
          }}

          void main() {{
            float minRes = min(uResolution.x, uResolution.y);
            float px = 1.0 / minRes;
            vec2 p = (gl_FragCoord.xy - 0.5 * uResolution.xy) * px;
            float cr = cos(uRotation), sr = sin(uRotation);
            p = mat2(cr, -sr, sr, cr) * p;
            p -= uMouse * uMouseInfluence;
            float sc = mix(1.0, uHoverScale, uHoverAmount) + uBurst * 0.3;
            p /= sc;
            vec3 c = vec3(0.0);
            float coverage = 0.0;
            float rcf = max(float(uRingCount) - 1.0, 1.0);
            for (int i = 0; i < 10; i++) {{
              if (i >= uRingCount) break;
              float fi = float(i);
              vec2 pr = p - fi * uParallax * uMouse;
              vec3 rc = mix(uColor, uColorTwo, fi / rcf);
              float ringAmount = ring(pr, uBaseRadius + fi * uRadiusStep, pow(uRingGap, fi), i == 0 ? 0.0 : 2.8 * fi, px);
              c = mix(c, rc, vec3(ringAmount));
              coverage = max(coverage, ringAmount);
            }}
            c *= 1.25 + uBurst * 2.0;
            float n = fract(sin(dot(gl_FragCoord.xy + uTime * 10.0, vec2(12.9898, 78.233))) * 43758.5453);
            c += (n - 0.5) * uNoiseAmount;
            float intensity = max(c.r, max(c.g, c.b));
            vec3 emissiveColor = intensity > 0.0001 ? clamp(c / intensity, 0.0, 1.0) : vec3(0.0);
            vec3 outputColor = mix(emissiveColor, clamp(c, 0.0, 1.0), uCoverageAlpha);
            float outputAlpha = mix(intensity, coverage, uCoverageAlpha);
            gl_FragColor = vec4(outputColor, clamp(outputAlpha * uOpacity, 0.0, 1.0));
          }}
        `;

        const container = document.getElementById('canvas-container');
        const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true, powerPreference: "high-performance" }});
        const dpr = Math.min(window.devicePixelRatio || 2, 2.5);
        renderer.setPixelRatio(dpr);
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-0.5, 0.5, 0.5, -0.5, 0.1, 10);
        camera.position.z = 1;

        const uniforms = {{
          uTime: {{ value: 0 }},
          uAttenuation: {{ value: 10.0 }},
          uResolution: {{ value: new THREE.Vector2(window.innerWidth * dpr, window.innerHeight * dpr) }},
          uColor: {{ value: new THREE.Color("{color}") }},
          uColorTwo: {{ value: new THREE.Color("{color_two}") }},
          uLineThickness: {{ value: 2.3 }},
          uBaseRadius: {{ value: 0.18 }},
          uRadiusStep: {{ value: 0.085 }},
          uScaleRate: {{ value: 0.075 }},
          uRingCount: {{ value: 8 }},
          uOpacity: {{ value: 1.0 }},
          uNoiseAmount: {{ value: 0.01 }},
          uRotation: {{ value: 0.0 }},
          uRingGap: {{ value: 1.4 }},
          uFadeIn: {{ value: 0.6 }},
          uFadeOut: {{ value: 0.4 }},
          uMouse: {{ value: new THREE.Vector2(0, 0) }},
          uMouseInfluence: {{ value: 0.15 }},
          uHoverAmount: {{ value: 0 }},
          uHoverScale: {{ value: 1.15 }},
          uParallax: {{ value: 0.03 }},
          uBurst: {{ value: 0 }},
          uCoverageAlpha: {{ value: 0 }},
        }};

        const material = new THREE.ShaderMaterial({{ vertexShader, fragmentShader, uniforms, transparent: true }});
        const quad = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
        scene.add(quad);

        let startT = performance.now();
        function animate() {{
          requestAnimationFrame(animate);
          uniforms.uTime.value = (performance.now() - startT) * 0.001;
          renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
          const w = window.innerWidth;
          const h = window.innerHeight;
          renderer.setSize(w, h);
          uniforms.uResolution.value.set(w * dpr, h * dpr);
        }});
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)


# ---------------------------------------------------------------------------
# SESSION ROUTER INITIALIZATION
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"
if "user_api_key" not in st.session_state:
    st.session_state["user_api_key"] = ""
if "uploaded_df" not in st.session_state:
    st.session_state["uploaded_df"] = None

# ---------------------------------------------------------------------------
# STEP 0: REAL USER AUTHENTICATION GATE (MAGIC RINGS 3D PORTAL)
# ---------------------------------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown("""
    <div class="login-fullscreen-wrapper">
        <div class="login-portal-title">GraphGuardians SOC</div>
        <div class="login-portal-sub">Financial Intelligence & Countermeasure Portal</div>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns([1, 2.2, 1])
    with col_r2:
        with st.form("real_auth_form"):
            st.markdown("<h4>Officer Authentication</h4>", unsafe_allow_html=True)
            username_input = st.text_input("Username", value="admin")
            password_input = st.text_input("Password", type="password", value="admin123")
            
            login_submit = st.form_submit_button("Authenticate Session", type="primary", use_container_width=True)

            if login_submit:
                user_record = db.authenticate_user(username_input, password_input)
                if user_record:
                    st.session_state["logged_in"] = True
                    st.session_state["user_info"] = user_record
                    st.session_state["current_page"] = "page1"

                    # Save login session
                    db.save_login(user_record["bank_name"], user_record["username"], user_record["officer_email"])

                    st.success(f"Authenticated session: {user_record['username']} ({user_record['role']})")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("Authentication failed. Invalid username or password.")
        st.markdown("<div style='text-align:center; font-family:\"Share Tech Mono\", monospace; color:#94a3b8; font-size:0.82rem; margin-top:16px;'>Default Credentials &mdash; Username: <b style='color:#a855f7;'>admin</b> | Password: <b style='color:#a855f7;'>admin123</b></div>", unsafe_allow_html=True)
    st.stop()



# ---------------------------------------------------------------------------
# TOP BANKING HEADER & NAVIGATION BAR
# ---------------------------------------------------------------------------
user_info = st.session_state.get("user_info") or {"bank_name": "GraphGuardians Bank", "username": "admin", "role": "Security Officer"}
st.markdown(f"""
<div class="bank-header">
    <div>
        <div class="bank-title">GraphGuardians SOC &middot; {user_info['bank_name']}</div>
        <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">Agentic Fraud Ring Detection & Countermeasure Engine</div>
    </div>
    <div class="bank-badge">
        Officer: {user_info['username']} ({user_info['role']})
    </div>
</div>
""", unsafe_allow_html=True)

# Page Router Navigation
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])

with col_nav1:
    if st.button("Step 1: Ingestion & Guide", use_container_width=True, type="primary" if st.session_state["current_page"] == "page1" else "secondary"):
        st.session_state["current_page"] = "page1"
        st.rerun()

with col_nav2:
    if st.button("Step 2: Fraud Intelligence Dashboard", use_container_width=True, type="primary" if st.session_state["current_page"] == "page2" else "secondary"):
        st.session_state["current_page"] = "page2"
        st.rerun()

with col_nav3:
    if st.button("Step 3: Audit Trail & Compliance", use_container_width=True, type="primary" if st.session_state["current_page"] == "page3" else "secondary"):
        st.session_state["current_page"] = "page3"
        st.rerun()

with col_nav4:
    if st.button("Sign Out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["current_page"] = "login"
        st.rerun()

st.markdown("<hr style='border-color:#334155; margin:16px 0 24px 0;'>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# GRAPH RENDERERS (CLEAR 3D WIRE VIEW & CLEAR 2D HIGH-CONTRAST VIEW)
# ---------------------------------------------------------------------------
def render_wire_3d_graph(G: nx.DiGraph, flagged_members: set, anomaly_scores: pd.Series, feature_contributions: dict, title: str = "3D Network Graph", only_fraud: bool = False):
    """Renders 3D Plotly network graph with crisp, glowing wire/circuit connections."""
    
    graph_to_render = G
    if only_fraud and len(flagged_members) > 0:
        graph_to_render = G.subgraph(flagged_members)

    if len(graph_to_render.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title=title, paper_bgcolor='#070a13', plot_bgcolor='#070a13', height=420)
        return fig

    # Compute 3D Spring Layout with wide node separation
    undirected = graph_to_render.to_undirected()
    pos_3d = nx.spring_layout(undirected, dim=3, seed=42, k=2.5, iterations=120)

    # Crisp Wire Connections
    edge_x, edge_y, edge_z = [], [], []
    for u, v in graph_to_render.edges():
        x0, y0, z0 = pos_3d[u]
        x1, y1, z1 = pos_3d[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_color = 'rgba(244, 63, 94, 0.85)' if only_fraud else 'rgba(245, 158, 11, 0.55)'
    edge_width = 3.5 if only_fraud else 2.2

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=edge_width, color=edge_color),
        hoverinfo='none',
        mode='lines',
        name='Transaction Wires'
    )

    fraud_x, fraud_y, fraud_z, fraud_txt = [], [], [], []
    normal_x, normal_y, normal_z, normal_txt = [], [], [], []

    for node in graph_to_render.nodes():
        x, y, z = pos_3d[node]
        score = float(anomaly_scores.get(node, 0.0))
        hover_html = get_account_hover_summary(node, feature_contributions, score)

        if node in flagged_members:
            fraud_x.append(x); fraud_y.append(y); fraud_z.append(z); fraud_txt.append(f"<b>Account: {node}</b><br>{hover_html}")
        else:
            normal_x.append(x); normal_y.append(y); normal_z.append(z); normal_txt.append(f"<b>Account: {node}</b><br>{hover_html}")

    data_traces = [edge_trace]

    if len(normal_x) > 0 and not only_fraud:
        normal_trace = go.Scatter3d(
            x=normal_x, y=normal_y, z=normal_z, mode='markers', name='Standard Account',
            hoverinfo='text', hovertext=normal_txt,
            marker=dict(size=6, color='#38bdf8', symbol='circle', opacity=0.85)
        )
        data_traces.append(normal_trace)

    if len(fraud_x) > 0:
        fraud_trace = go.Scatter3d(
            x=fraud_x, y=fraud_y, z=fraud_z, mode='markers', name='High-Risk Fraud Account',
            hoverinfo='text', hovertext=fraud_txt,
            marker=dict(size=13, color='#f43f5e', symbol='diamond', line=dict(width=2, color='#ffffff'))
        )
        data_traces.append(fraud_trace)

    fig = go.Figure(
        data=data_traces,
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18, color='#f8fafc')),
            showlegend=True,
            legend=dict(
                font=dict(color='#e2e8f0'),
                bgcolor='rgba(15, 23, 42, 0.85)',
                bordercolor='#334155',
                borderwidth=1,
                x=0.01, y=0.99
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor='#070a13',
            plot_bgcolor='#070a13',
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                bgcolor='#070a13',
                camera=dict(eye=dict(x=1.7, y=1.7, z=1.4))
            ),
            height=580
        )
    )
    return fig


def render_wire_2d_graph(G: nx.DiGraph, flagged_members: set, anomaly_scores: pd.Series, feature_contributions: dict, title: str = "2D High-Contrast Network Graph", only_fraud: bool = False):
    """Renders 2D Plotly network graph with explicit account node labels and crisp connection lines."""
    
    graph_to_render = G
    if only_fraud and len(flagged_members) > 0:
        graph_to_render = G.subgraph(flagged_members)

    if len(graph_to_render.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title=title, paper_bgcolor='#070a13', plot_bgcolor='#070a13', height=420)
        return fig

    undirected = graph_to_render.to_undirected()
    pos_2d = nx.spring_layout(undirected, seed=42, k=0.6, iterations=100)

    edge_x, edge_y = [], []
    for u, v in graph_to_render.edges():
        x0, y0 = pos_2d[u]
        x1, y1 = pos_2d[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_color = 'rgba(244, 63, 94, 0.85)' if only_fraud else 'rgba(245, 158, 11, 0.55)'
    edge_width = 3.0 if only_fraud else 1.8

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=edge_width, color=edge_color),
        hoverinfo='none',
        mode='lines',
        name='Transaction Connections'
    )

    normal_nodes = [n for n in graph_to_render.nodes() if n not in flagged_members]
    fraud_nodes = [n for n in graph_to_render.nodes() if n in flagged_members]

    data_traces = [edge_trace]

    if normal_nodes and not only_fraud:
        nx_norm = [pos_2d[n][0] for n in normal_nodes]
        ny_norm = [pos_2d[n][1] for n in normal_nodes]
        txt_norm = [f"<b>Account: {n}</b><br>{get_account_hover_summary(n, feature_contributions, float(anomaly_scores.get(n, 0.0)))}" for n in normal_nodes]
        labels_norm = [str(n) if len(graph_to_render.nodes) <= 60 else "" for n in normal_nodes]

        normal_trace = go.Scatter(
            x=nx_norm, y=ny_norm, mode='markers+text', name='Standard Account',
            hoverinfo='text', hovertext=txt_norm,
            text=labels_norm, textposition="top center",
            textfont=dict(color="#94a3b8", size=9),
            marker=dict(size=11, color='#38bdf8', symbol='circle', line=dict(width=1.5, color='#0284c7'))
        )
        data_traces.append(normal_trace)

    if fraud_nodes:
        fx_fraud = [pos_2d[n][0] for n in fraud_nodes]
        fy_fraud = [pos_2d[n][1] for n in fraud_nodes]
        txt_fraud = [f"<b>Account: {n}</b><br>{get_account_hover_summary(n, feature_contributions, float(anomaly_scores.get(n, 0.0)))}" for n in fraud_nodes]
        labels_fraud = [str(n) for n in fraud_nodes]

        fraud_trace = go.Scatter(
            x=fx_fraud, y=fy_fraud, mode='markers+text', name='High-Risk Fraud Account',
            hoverinfo='text', hovertext=txt_fraud,
            text=labels_fraud, textposition="top center",
            textfont=dict(color="#f87171", size=11, family="Share Tech Mono"),
            marker=dict(size=18, color='#f43f5e', symbol='diamond', line=dict(width=2, color='#ffffff'))
        )
        data_traces.append(fraud_trace)

    fig = go.Figure(
        data=data_traces,
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18, color='#f8fafc')),
            showlegend=True,
            legend=dict(
                font=dict(color='#e2e8f0'),
                bgcolor='rgba(15, 23, 42, 0.85)',
                bordercolor='#334155',
                borderwidth=1,
                x=0.01, y=0.99
            ),
            margin=dict(l=20, r=20, b=20, t=50),
            paper_bgcolor='#070a13',
            plot_bgcolor='#070a13',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=580
        )
    )
    return fig


# ===========================================================================
# PAGE 1 — INGESTION & INPUT DATASET SETUP PAGE
# ===========================================================================
if st.session_state["current_page"] == "page1":
    st.markdown("### Architecture Overview & Pipeline Guide")
    st.markdown("Multi-Agent Architecture: **DetectorAgent** &rarr; **InvestigatorAgent** &rarr; **CountermeasureAgent**.")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        <div class="guide-card">
            <div class="step-number">01 / STEP</div>
            <div class="step-title">Upload Financial Transaction Dataset</div>
            <div class="step-desc">Upload bank transaction CSV dataset. Auto-detects sender, receiver, and transfer amount schema.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="guide-card">
            <div class="step-number">03 / STEP</div>
            <div class="step-title">Investigator Reasoning & Risk Tiering</div>
            <div class="step-desc">Classifies risk severity into tiers (CRITICAL, HIGH, MEDIUM, LOW) with structured feature contribution explanations.</div>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div class="guide-card">
            <div class="step-number">02 / STEP</div>
            <div class="step-title">Detector Machine Learning Core</div>
            <div class="step-desc">IsolationForest anomaly scoring + Louvain graph modularity algorithms flag colluding money-mule rings.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="guide-card">
            <div class="step-number">04 / STEP</div>
            <div class="step-title">Autonomous Countermeasure Execution</div>
            <div class="step-desc">Auto-freezes CRITICAL accounts, revokes session tokens, generates downloadable FinCEN SAR reports, and logs human overrides.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Step 1: Input Dataset Selection & Ingestion")
    
    with st.expander("Upload Custom CSV Dataset or Load Benchmark Data", expanded=True):
        st.markdown("##### Select Dataset Source Mode:")

        mode_choice = st.radio(
            "Select Data Source Mode:",
            ["Upload Custom CSV Dataset", "Default PaySim Financial Dataset", "Synthetic Mule Ring Dataset"],
            horizontal=True
        )

        curr_df = st.session_state.get("uploaded_df")

        if mode_choice == "Upload Custom CSV Dataset":
            uploaded_file = st.file_uploader("Upload Bank Transaction File (.csv)", type=["csv"])
            if uploaded_file is not None:
                try:
                    curr_df = pd.read_csv(uploaded_file)
                    st.session_state["uploaded_df"] = curr_df
                    st.success(f"Successfully loaded dataset: {uploaded_file.name} ({len(curr_df):,} rows)")
                except Exception as e:
                    st.error(f"Error parsing CSV file: {e}")

        elif mode_choice == "Default PaySim Financial Dataset":
            curr_df = load_transactions()
            st.session_state["uploaded_df"] = curr_df
            st.info(f"Loaded PaySim Dataset ({len(curr_df):,} transactions)")

        elif mode_choice == "Synthetic Mule Ring Dataset":
            curr_df = load_transactions(n_synthetic=2500)
            st.session_state["uploaded_df"] = curr_df
            st.info(f"Loaded Synthetic Mule Ring Dataset ({len(curr_df):,} transactions)")

        # Display Dataset Summary & Auto-Detected Schema
        if curr_df is not None:
            st.markdown("---")
            st.markdown("##### Ingested Dataset Metrics & Auto-Detected Schema:")

            orig_col, dest_col, amt_col = detect_transaction_columns(curr_df)

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Total Transactions", f"{len(curr_df):,}")
            with col_s2:
                sender_cnt = curr_df[orig_col].nunique() if orig_col in curr_df else 0
                st.metric("Sender Accounts", f"{sender_cnt:,}")
            with col_s3:
                dest_cnt = curr_df[dest_col].nunique() if dest_col in curr_df else 0
                st.metric("Receiver Accounts", f"{dest_cnt:,}")
            with col_s4:
                try:
                    total_vol = float(curr_df[amt_col].sum()) if amt_col in curr_df else 0.0
                    st.metric("Total Volume Moved", f"₹{total_vol/100000.0:,.1f}L")
                except Exception:
                    st.metric("Total Volume Moved", "N/A")

            st.caption(f"Auto-Detected Schema: Sender = `{orig_col}` | Receiver = `{dest_col}` | Amount = `{amt_col}`")

            with st.expander("Inspect Dataset Sample (First 5 Rows)"):
                st.dataframe(curr_df.head(5), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Initiate Fraud Detection Pipeline", type="primary", use_container_width=True):
                st.session_state["current_page"] = "page2"
                st.session_state["trigger_analysis"] = True
                st.rerun()


# ===========================================================================
# PAGE 2 — MAIN ANALYSIS DASHBOARD & DYNAMIC ACCOUNT FREEZE PANEL
# ===========================================================================
elif st.session_state["current_page"] == "page2":
    
    df = st.session_state.get("uploaded_df")
    if df is None:
        df = load_transactions()
        st.session_state["uploaded_df"] = df

    # SIDEBAR CONTROLS
    st.sidebar.header("Agent Parameters")
    risk_threshold = st.sidebar.slider("Risk Cutoff Threshold", 0.20, 0.90, 0.55, step=0.05)
    contamination = st.sidebar.slider("IsolationForest Contamination", 0.01, 0.25, 0.10, step=0.01)

    st.sidebar.markdown("---")
    st.sidebar.markdown("##### Ingest New Dataset")
    sidebar_file = st.sidebar.file_uploader("Upload New Dataset (.csv)", type=["csv"], key="sidebar_csv")
    if sidebar_file is not None:
        try:
            df = pd.read_csv(sidebar_file)
            st.session_state["uploaded_df"] = df
            st.sidebar.success("New CSV Loaded!")
        except Exception as e:
            st.sidebar.error(f"Upload error: {e}")

    # Live Stream Feed Simulation Mode Toggle
    simulate_live = st.sidebar.toggle("Simulate Live Stream Feed Mode", value=False)

    st.sidebar.markdown("---")
    run_pipeline_btn = st.sidebar.button("Re-Run Fraud Engine", type="primary", use_container_width=True)

    if run_pipeline_btn:
        st.session_state["trigger_analysis"] = True

    # TRIGGER AGENTIC PIPELINE EXECUTION ON THE USER INPUT DATASET
    if st.session_state.get("trigger_analysis", False):
        st.markdown("### Processing Transaction Network Graph...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        steps = [
            ("Step 1/4 DetectorAgent: Parsing transaction dataset & mapping graph topology...", 25),
            ("Step 2/4 DetectorAgent: Computing IsolationForest & Louvain graph community scores...", 50),
            ("Step 3/4 InvestigatorAgent: Evaluating feature attributions & risk severity classification...", 75),
            ("Step 4/4 CountermeasureAgent: Executing auto-freezes, token revocations, and SAR drafts...", 100),
        ]

        for msg, val in steps:
            status_text.markdown(f"**{msg}**")
            progress_bar.progress(val)
            time.sleep(0.2)

        # Execute Multi-Step Agent Pipeline on the user uploaded dataset!
        agent_results = agents.run_agentic_pipeline(
            df=df,
            bank_name=user_info["bank_name"],
            risk_threshold=risk_threshold,
            contamination=contamination,
            user_api_key=st.session_state.get("user_api_key", "")
        )

        st.session_state["agent_results"] = agent_results
        st.session_state["trigger_analysis"] = False
        st.rerun()

    # IF PIPELINE NOT RUN YET
    if "agent_results" not in st.session_state:
        st.info("Dataset loaded. Click 'Initiate Fraud Detection Pipeline' below to execute analysis.")
        if st.button("Initiate Fraud Detection Pipeline", type="primary", use_container_width=True):
            st.session_state["trigger_analysis"] = True
            st.rerun()
        st.stop()

    res = st.session_state["agent_results"]
    G = res["G"]
    anomaly_scores = res["anomaly_scores"]
    community_report = res["community_report"]
    flagged_rings = res["flagged_rings"]
    feature_contributions = res["feature_contributions"]
    ring_analyses = res["ring_analyses"]
    batch_id = res["batch_id"]

    # LIVE STREAM SIMULATION
    if simulate_live:
        st.info("Live Stream Feed Active: Replaying streaming transaction feed...")

    # DATABASE CONFIRMATION BADGE
    st.markdown(f'<div class="db-badge">State Persisted to SQLite Database (Batch #{batch_id})</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # TOP KPI STRIP (TOTAL SCAM AMOUNT & ACCOUNTS TO FREEZE FROM USER DATASET)
    # ---------------------------------------------------------------------------
    total_accounts = G.number_of_nodes()
    flagged_count = len(flagged_rings)
    total_amount_scammed = flagged_rings["total_amount_moved"].sum() if flagged_count > 0 else 0.0
    scam_in_lakhs = total_amount_scammed / 100000.0

    flagged_members = set()
    for members in flagged_rings["members"]:
        flagged_members.update(members)
        
    freeze_accounts_count = len(flagged_members)

    st.markdown(f"""
    <div class="tva-kpi-row">
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Accounts Monitored</div>
            <div class="tva-kpi-value">{total_accounts:,}</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Flagged Fraud Rings</div>
            <div class="tva-kpi-value danger">{flagged_count}</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Total Amount Scammed</div>
            <div class="tva-kpi-value danger">&#8377;{scam_in_lakhs:.1f}L</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Accounts To Freeze</div>
            <div class="tva-kpi-value danger">{freeze_accounts_count} Accounts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # MAIN DASHBOARD: DUAL CLEAR GRAPH VIEWS & DYNAMIC FREEZE PANEL
    # ---------------------------------------------------------------------------
    c_left, c_right = st.columns([1.45, 1.0])

    with c_left:
        st.markdown("#### Transaction Network Topology Visualizer")
        
        # Dual View Mode Selector (3D Wire View vs 2D High-Contrast View)
        view_tab = st.radio("Select Visualization Mode:", ["3D Fiber-Optic Wire View", "2D High-Contrast Interactive View"], horizontal=True)

        if "3D" in view_tab:
            st.markdown("##### 1. Overall Account Network Topology (All Accounts)")
            st.caption("Hover over nodes for anomaly scores & key behavioral attribution metrics")
            fig_overall = render_wire_3d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="Overall Account Network Topology (3D Wire View)", only_fraud=False
            )
            st.plotly_chart(fig_overall, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("##### 2. Isolated High-Risk Fraud Accounts Subgraph")
            st.caption("Plotting target fraud ring accounts in the active dataset")
            fig_fraud = render_wire_3d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="High-Risk Fraud Accounts Subgraph (3D View)", only_fraud=True
            )
            st.plotly_chart(fig_fraud, use_container_width=True)

        else:
            st.markdown("##### 1. Overall Account Network Topology (2D View)")
            st.caption("High-contrast node layout with account labels on hover & zoom")
            fig_overall_2d = render_wire_2d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="Overall Account Network Topology (2D View)", only_fraud=False
            )
            st.plotly_chart(fig_overall_2d, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("##### 2. Isolated High-Risk Fraud Accounts Subgraph (2D View)")
            st.caption("High-contrast subgraph of target fraud ring accounts")
            fig_fraud_2d = render_wire_2d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="High-Risk Fraud Accounts Subgraph (2D View)", only_fraud=True
            )
            st.plotly_chart(fig_fraud_2d, use_container_width=True)

    with c_right:
        # AGENT ACTIONS & ACCOUNT FREEZE PANEL
        st.markdown("#### Agent Actions & Account Protection Panel")
        st.caption("Proactive countermeasures generated for accounts in current dataset")

        if flagged_count > 0:
            # Download Full Risk CSV Report Button
            csv_data = community_report.to_csv(index=False)
            st.download_button(
                label="Export Community Risk Report (.CSV)",
                data=csv_data,
                file_name="Fraud_Community_Risk_Report.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            for r_id, analysis in ring_analyses.items():
                tier = analysis["tier"]
                reasoning = analysis["reasoning"]
                cm = analysis["countermeasures"]
                r_data = analysis["ring_data"]

                target_accs_str = ", ".join(r_data['members'])

                st.markdown(f"""
                <div class="agent-action-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <strong style="font-size:1.05rem;">Fraud Ring #{r_id} ({r_data['size']} Accounts)</strong>
                        <span class="tier-badge tier-{tier}">{tier} SEVERITY</span>
                    </div>
                    <p style="font-size:0.85rem; color:#d6d3d1; margin-bottom:6px;"><b>Total Volume:</b> ₹{r_data['total_amount_moved']:,.2f}</p>
                    <p style="font-size:0.85rem; color:#d6d3d1; margin-bottom:8px;"><b>Investigator Reasoning:</b> {reasoning}</p>
                    <p style="font-size:0.82rem; color:#f43f5e; margin-bottom:8px; font-family:Share Tech Mono, monospace;"><b>Target Accounts to Freeze:</b><br>{target_accs_str}</p>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
                        • Executed Actions: {len(cm['executed_actions'])} | Pending Approval: {len(cm['pending_actions'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # HUMAN OVERRIDE CONTROLS (FREEZE / UNFREEZE ACTIONS)
                db_actions = db.fetch_actions_for_batch(batch_id)
                ring_actions = [a for a in db_actions if a["ring_id"] == r_id]

                if ring_actions:
                    with st.expander(f"Manage Actions & Overrides (Ring #{r_id})"):
                        for act in ring_actions:
                            act_id = act["id"]
                            status = act["status"]
                            acc_id = act["account_id"]
                            a_type = act["action_type"]

                            st.write(f"• **{a_type}** for `{acc_id}` — Status: `{status}`")
                            
                            b_col1, b_col2 = st.columns(2)
                            with b_col1:
                                if status == "PENDING_APPROVAL":
                                    if st.button(f"Enforce Account Freeze ({acc_id})", key=f"app_{act_id}"):
                                        db.approve_pending_action(act_id, approved_by=user_info["username"])
                                        st.success(f"Enforced account freeze for {acc_id}")
                                        st.rerun()
                            with b_col2:
                                if status in ["EXECUTED", "PENDING_APPROVAL"]:
                                    if st.button(f"Reverse Action / Unfreeze", key=f"rev_{act_id}"):
                                        db.reverse_action(act_id, approved_by=user_info["username"])
                                        countermeasures.unfreeze_account(acc_id, approved_by=user_info["username"])
                                        st.warning(f"Reversed freeze for {acc_id}")
                                        st.rerun()

                # DOWNLOAD SAR REPORT BUTTON FOR THIS SPECIFIC RING IN USER DATASET
                sar_path = cm.get("sar_file_path", "")
                if sar_path and os.path.exists(sar_path):
                    with open(sar_path, "r", encoding="utf-8") as f:
                        sar_text = f.read()
                    st.download_button(
                        label=f"Export FinCEN SAR Regulatory Filing (Ring #{r_id})",
                        data=sar_text,
                        file_name=f"FinCEN_SAR_Report_Ring_{r_id}.txt",
                        mime="text/plain",
                        key=f"sar_dl_{r_id}"
                    )
                st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.success("Security Status Clean: No fraud rings detected in current dataset.")


# ===========================================================================
# PAGE 3 — ABOUT & AUDIT TRAIL PAGE
# ===========================================================================
elif st.session_state["current_page"] == "page3":
    st.markdown("### System Architecture & Audit Trail")
    st.markdown("GraphGuardians Enterprise Fraud Intelligence Engine.")

    st.markdown("#### Mission & Design Principles")
    st.info("""
    **Core Objective**: Traditional rules-based fraud engines fail against modern colluding money-mule networks. 
    By combining **Unsupervised Machine Learning (IsolationForest)** with **Graph Modularity Analytics (Louvain Algorithm)**, 
    **Multi-Agent Reasoning (Detector &rarr; Investigator &rarr; Countermeasure)**, and **Real State Persistence**, 
    GraphGuardians empowers financial security operations teams to isolate and neutralize complex fraud networks in real time.
    """)

    st.markdown("---")
    st.markdown("#### Engineering Team")

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div class="step-title">Lead AI / ML Engineer</div>
            <div class="step-desc">Designed IsolationForest Anomaly Engine, Feature Attribution, & Louvain Graph Analytics.</div>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div class="step-title">Countermeasure Architecture Lead</div>
            <div class="step-desc">Architected Countermeasure Engine, SQLite Persistence, and Human Override Controls.</div>
        </div>
        """, unsafe_allow_html=True)

    with t3:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div class="step-title">Multi-Agent Pipeline Lead</div>
            <div class="step-desc">Orchestrated DetectorAgent, InvestigatorAgent, and CountermeasureAgent reasoning chain.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### SQLite Countermeasure Actions Audit Log")
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions ORDER BY id DESC LIMIT 20;")
    action_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if action_rows:
        st.dataframe(pd.DataFrame(action_rows), use_container_width=True)
    else:
        st.caption("No countermeasure actions logged in SQLite database yet.")

    st.markdown("#### SQLite Analysis Batches Audit Log")
    recent_records = db.fetch_latest_records(5)
    if recent_records:
        st.dataframe(pd.DataFrame(recent_records), use_container_width=True)
    else:
        st.caption("No historical records saved in SQLite yet.")
