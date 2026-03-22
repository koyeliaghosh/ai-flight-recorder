import streamlit as st
import pandas as pd
import mlflow
from src.agent import run_agent
from src.replay import fetch_recent_runs, replay_run

st.set_page_config(page_title="AI Flight Recorder", layout="wide")

st.title("🛫 AI Flight Recorder for Agents")
st.markdown("Not just logging → **diagnosis + replay**. Not just observability → **actionable improvement**. Not just experiment tracking → **agent-level trace intelligence**.")

# Setup MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Agent_Flight_Recorder")

tab1, tab2, tab3 = st.tabs(["Query", "Trace Dashboard", "Replay & Comparison"])

with tab1:
    st.header("Agent Query")
    query = st.text_area("Enter your query (e.g., 'Reconcile PO-888 against Invoice 5678')")
    prompt_version = st.selectbox("Prompt Version", ["v1", "v2-adversarial"])
    
    if st.button("Run Agent"):
        with st.spinner("Running agent with strict 2-try limit..."):
            with mlflow.start_run(run_name="UI_Agent_Run"):
                result = run_agent(query=query, prompt_version=prompt_version, max_tries=2)
            st.success("Run complete!")
            st.json(result)

with tab2:
    st.header("Trace Dashboard")
    st.info("Fetching traces exclusively from MLflow.")
    if st.button("Refresh Dashboard"):
        # We allow a larger limit for general dashboard viewing
        runs = fetch_recent_runs(limit=10)
        if runs:
            st.dataframe(pd.DataFrame(runs)[["run_id", "status", "start_time", "params.query", "params.prompt_version"]])
        else:
            st.write("No traces found.")

with tab3:
    st.header("Replay & Comparison")
    st.info("Strictly limits replay history and comparison to exactly 2 runs.")
    
    recent_runs = fetch_recent_runs(limit=2)
    if len(recent_runs) < 1:
        st.write("Not enough runs to display replay. Run a query first.")
    else:
        run_options = {r["run_id"]: f"{r['run_id']} - {r.get('params.query', 'No Query')}" for r in recent_runs}
        selected_run_id = st.selectbox("Select Run to Replay", list(run_options.keys()), format_func=lambda x: run_options[x])
        new_prompt = st.selectbox("Change Prompt Version for Replay", ["v1", "v2-adversarial", "v3-strict"])
        
        if st.button("Replay Run"):
            with st.spinner("Replaying..."):
                replay_res = replay_run(selected_run_id, new_prompt)
                st.session_state["last_replay"] = {
                    "original": selected_run_id,
                    "replay": replay_res
                }
                
        if "last_replay" in st.session_state:
            st.subheader("Comparison (Exactly 2 Runs)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Run A (Original)", st.session_state["last_replay"]["original"])
                orig_run = mlflow.get_run(st.session_state["last_replay"]["original"])
                st.json(orig_run.data.params)
                st.write(orig_run.data.tags.get("agent.final_response"))
            with col2:
                new_run_id = st.session_state["last_replay"]["replay"]["new_run_id"]
                st.metric("Run B (Replay)", new_run_id)
                new_run = mlflow.get_run(new_run_id)
                st.json(new_run.data.params)
                st.write(new_run.data.tags.get("agent.final_response"))
