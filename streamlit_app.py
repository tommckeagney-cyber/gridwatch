import streamlit as st
import anthropic

st.set_page_config(page_title="AI Test")

st.title("🔧 AI Connection Test")

# Check if anthropic is installed
try:
    import anthropic
    st.success("✅ anthropic package is installed")
except ImportError:
    st.error("❌ anthropic package is NOT installed")

# Check secrets
try:
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if api_key:
        st.success(f"✅ API key found: {api_key[:10]}...")
        
        # Try to connect
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": "Say 'Connection successful!'"}]
            )
            st.success(f"✅ API connection successful! Response: {response.content[0].text}")
        except Exception as e:
            st.error(f"❌ API connection failed: {e}")
    else:
        st.error("❌ No API key found in secrets")
except Exception as e:
    st.error(f"❌ Error reading secrets: {e}")
