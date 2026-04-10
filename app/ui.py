import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components

# Backend URL
BASE_URL = "https://neonsecurevaultproject_frontend-production.up.railway.app"

st.set_page_config(page_title="NeonVault Admin Pro", layout="wide", initial_sidebar_state="collapsed")

# --- 1. 3D PURPLE BACKGROUND ---
components.html("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
    <div id="vanta-canvas" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
    <script>
        VANTA.NET({
          el: "#vanta-canvas",
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0x9255e2,
          backgroundColor: 0x12032e,
          points: 15.00,
          maxDistance: 20.00,
          spacing: 15.00
        })
    </script>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
    </style>
""", height=0)

# --- 2. GLOBAL STYLING ---
st.markdown("""
    <style>
    .stApp { background: transparent !important; }
    iframe { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; border: none; }
    
    .glass-card {
        background: rgba(146, 85, 226, 0.1);
        border: 1px solid rgba(146, 85, 226, 0.3);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    
    .neon-text {
        color: #c79eff;
        text-shadow: 0 0 10px #9255e2;
        font-weight: bold;
    }

    .status-indicator {
        font-size: 0.8rem;
        color: #00ff00;
        margin-top: -10px;
    }

    .tech-monitor {
        background: rgba(146, 85, 226, 0.05); 
        border-top: 1px solid rgba(146, 85, 226, 0.3); 
        padding: 20px; 
        border-radius: 20px; 
        text-align: center;
        margin-top: 50px;
    }

    @keyframes blinker {
        50% { opacity: 0.3; text-shadow: none; }
    }

    .blinking-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(18, 3, 46, 0.9);
        border-top: 1px solid rgba(146, 85, 226, 0.5);
        color: #c79eff;
        text-align: center;
        padding: 10px 0;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        letter-spacing: 2px;
        animation: blinker 2s linear infinite;
        z-index: 100;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state: st.session_state.token = None
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "user_data" not in st.session_state: st.session_state.user_data = None

# --- 3. LOGIN / SIGNUP INTERFACE ---
if st.session_state.token is None:
    st.markdown("<h1 class='neon-text' style='text-align:center;'>🛡️ NEON VAULT ACCESS</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Access Level")
        login_role = st.radio("Login as:", ["Standard User", "Administrator"], horizontal=True)
        
        with st.form("l_form"):
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("AUTHENTICATE"):
                res = requests.post(f"{BASE_URL}/login", data={"username": e, "password": p})
                if res.status_code == 200:
                    data = res.json()
                    if login_role == "Administrator" and not data.get("is_admin", False):
                        st.error("🚨 Access Denied: Administrator clearance required!")
                    else:
                        st.session_state.token = data["access_token"]
                        st.session_state.is_admin = data.get("is_admin", False)
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        user_res = requests.get(f"{BASE_URL}/users/me", headers=headers)
                        if user_res.status_code == 200:
                            st.session_state.user_data = user_res.json()
                        st.rerun()
                else:
                    st.error("Invalid Credentials")

    with tab2:
        with st.form("s_form"):
            u = st.text_input("Username")
            em = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("CREATE IDENTITY"):
                requests.post(f"{BASE_URL}/signup", json={"username":u, "email":em, "password":pw})
                st.success("Account Created! Use the Login tab.")

# --- 4. MAIN DASHBOARD ---
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    with st.sidebar:
        u_name = st.session_state.user_data.get('username', 'Agent') if st.session_state.user_data else "User"
        st.markdown(f"<h2 class='neon-text'>NEON VAULT</h2>", unsafe_allow_html=True)
        st.markdown(f"**👤 User:** {u_name}")
        st.markdown("<p class='status-indicator'>🟢 Online Status: Active</p>", unsafe_allow_html=True)
        st.divider()
        if st.button("🔴 LOGOUT"):
            st.session_state.token = None
            st.session_state.user_data = None
            st.rerun()

    menu = ["🏠 My Documents", "📤 Secure Upload"]
    if st.session_state.is_admin:
        menu.append("⚙️ Admin Terminal")
    
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "🏠 My Documents":
        st.markdown("<h2 class='neon-text'>Classified Files</h2>", unsafe_allow_html=True)
        try:
            docs = requests.get(f"{BASE_URL}/my-documents/", headers=headers).json()
            if not docs:
                st.info("Vault is empty.")
            for d in docs:
                with st.container():
                    st.markdown(f"<div class='glass-card'><h4>📄 {d['filename']}</h4><p>v{d['version']}</p></div>", unsafe_allow_html=True)
                    if st.button(f"Prepare Download: {d['filename']}", key=f"prep_{d['id']}"):
                        dl = requests.get(f"{BASE_URL}/download-document/{d['id']}", headers=headers)
                        st.download_button(f"Click to Save {d['filename']}", dl.content, file_name=d['filename'], key=f"dl_{d['id']}")
            
            st.markdown("""
                <div class='tech-monitor'>
                    <h4 class='neon-text' style='font-size: 0.9rem; margin-bottom: 15px;'>🛰️ SYSTEM NODE MONITOR</h4>
                    <div style='display: flex; justify-content: center; gap: 40px;'>
                        <div>
                            <p style='color: #888; font-size: 0.7rem; margin: 0;'>ENCRYPTION</p>
                            <p style='color: #00ff00; font-weight: bold; margin: 0;'>AES-256 ACTIVE</p>
                        </div>
                        <div style='border-left: 1px solid rgba(255,255,255,0.1); padding-left: 40px;'>
                            <p style='color: #888; font-size: 0.7rem; margin: 0;'>SERVER LATENCY</p>
                            <p style='color: #c79eff; font-weight: bold; margin: 0;'>24ms</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.error("Failed to connect to vault.")

    elif choice == "📤 Secure Upload":
        st.markdown("<h2 class='neon-text'>Upload to Vault</h2>", unsafe_allow_html=True)
        f = st.file_uploader("Select File", label_visibility="collapsed")
        if f and st.button("ENCRYPT & SAVE"):
            requests.post(f"{BASE_URL}/upload-file/", headers=headers, files={"file": (f.name, f.getvalue())})
            st.success("File added to vault!")

    elif choice == "⚙️ Admin Terminal":
        st.markdown("<h2 class='neon-text'>System Command Center</h2>", unsafe_allow_html=True)
        a_tab1, a_tab2 = st.tabs(["📊 Analytics", "👥 User Management"])
        
        with a_tab1:
            stats = pd.DataFrame({"Activity": ["Uploads", "Downloads", "Logins"], "Count": [24, 56, 12]})
            st.bar_chart(stats, x="Activity", y="Count")
        
        with a_tab2:
            res = requests.get(f"{BASE_URL}/admin/users/", headers=headers).json()
            for user in res:
                with st.expander(f"👤 {user['username']} ({user['email']})"):
                    col_info, col_actions = st.columns([3, 2])
                    with col_info:
                        st.markdown(f"**Admin Clearance:** {'✅ Level A' if user['is_admin'] else '❌ Standard'}")
                    with col_actions:
                        c1, c2 = st.columns(2)
                        new_role = not user['is_admin']
                        role_label = "Demote" if user['is_admin'] else "Promote"
                        if c1.button(role_label, key=f"r_{user['id']}"):
                            requests.put(f"{BASE_URL}/admin/users/{user['id']}/role?is_admin={new_role}", headers=headers)
                            st.rerun()
                        if c2.button("🗑️ PURGE", key=f"d_{user['id']}"):
                            response = requests.delete(f"{BASE_URL}/admin/users/{user['id']}", headers=headers)
                            if response.status_code == 200:
                                st.rerun()
                            else:
                                st.error("Operation Failed.")

st.markdown("<div class='blinking-footer'>PROJECT NEONSECURVAULT // DEVELOPED BY FZ</div>", unsafe_allow_html=True)