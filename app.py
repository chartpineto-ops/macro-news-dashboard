import feedparser
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Macro News Dashboard", layout="wide")

st_autorefresh(interval=60 * 1000, key="news_refresh")

st.title("Macro News Dashboard")
st.caption("Auto-refreshing macro headlines")

FEEDS = {
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
    "CNBC World": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "MarketWatch Top Stories": "http://feeds.marketwatch.com/marketwatch/topstories/"
}

@st.cache_data(ttl=300)
def load_feed(url, source_name):
    feed = feedparser.parse(url)
    rows = []

    for entry in feed.entries[:20]:
        rows.append({
            "source": source_name,
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")
        })

    return rows

all_rows = []
for source_name, url in FEEDS.items():
    try:
        all_rows.extend(load_feed(url, source_name))
    except Exception as e:
        st.warning(f"Could not load {source_name}: {e}")

df = pd.DataFrame(all_rows)

if df.empty:
    st.error("No headlines loaded.")
    st.stop()

keyword = st.text_input("Filter headlines by keyword", "")

if keyword:
    df = df[
        df["title"].str.contains(keyword, case=False, na=False) |
        df["summary"].str.contains(keyword, case=False, na=False)
    ]

df = df.drop_duplicates(subset=["title", "source"])

st.subheader("Latest Headlines")

for _, row in df.iterrows():
    st.markdown(f"**{row['source']}**")
    st.markdown(f"[{row['title']}]({row['link']})")
    if row["published"]:
        st.caption(f"Published: {row['published']}")
    st.divider()

with st.expander("Show raw table"):
    st.dataframe(df, use_container_width=True)
