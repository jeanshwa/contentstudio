import streamlit as st
import anthropic
import json
import re
from datetime import datetime

# ─── Page config ───
st.set_page_config(
    page_title="律师内容工厂 | Legal Content Studio",
    page_icon="⚖️",
    layout="centered",
)

# ─── Custom CSS for mobile-friendly + WeChat/小红书 aesthetic ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');

/* Global */
.stApp {
    font-family: 'Noto Sans SC', sans-serif;
}

/* Header */
.app-header {
    background: linear-gradient(135deg, #d4380d 0%, #ff6b35 100%);
    color: white;
    padding: 1.5rem 1.2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    text-align: center;
}
.app-header h1 {
    font-size: 1.6rem;
    font-weight: 900;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.app-header p {
    font-size: 0.85rem;
    opacity: 0.9;
    margin: 0;
}

/* Content card */
.content-card {
    background: #fffbf5;
    border: 1px solid #ffe0cc;
    border-radius: 14px;
    padding: 1.2rem;
    margin: 1rem 0;
    line-height: 1.85;
    font-size: 0.95rem;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* News summary card */
.news-card {
    background: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: 14px;
    padding: 1.2rem;
    margin: 1rem 0;
    font-size: 0.88rem;
    line-height: 1.7;
}
.news-card h4 {
    color: #389e0d;
    margin: 0 0 0.5rem 0;
    font-size: 0.95rem;
}

/* Copy button area */
.copy-area {
    margin: 0.5rem 0 1.5rem 0;
}

/* Platform tabs styling */
.platform-tag {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.tag-xhs {
    background: #ff2442;
    color: white;
}
.tag-wechat {
    background: #07c160;
    color: white;
}

/* Section labels */
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #8c8c8c;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.5rem 0 0.5rem 0;
}

/* Divider */
.fancy-divider {
    text-align: center;
    margin: 2rem 0;
    color: #d9d9d9;
    font-size: 0.8rem;
    letter-spacing: 4px;
}

/* Mobile optimization */
@media (max-width: 768px) {
    .stApp {
        padding: 0.2rem;
    }
    .content-card {
        font-size: 0.92rem;
        padding: 1rem;
    }
}

/* Hide default Streamlit header/footer for cleaner mobile look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Button styling */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ───
st.markdown("""
<div class="app-header">
    <h1>⚖️ 律师内容工厂</h1>
    <p>一键抓取新闻 → AI生成爆款帖 → 复制粘贴发布</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar: API key ───
with st.sidebar:
    st.markdown("### ⚙️ 设置 Settings")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="在 console.anthropic.com 获取你的 API key",
        value=st.session_state.get("api_key", ""),
    )
    if api_key:
        st.session_state["api_key"] = api_key

    # Show status
    has_secret = False
    try:
        has_secret = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        pass
    if api_key:
        st.success("✅ API Key 已输入", icon="✅")
    elif has_secret:
        st.success("✅ API Key 已从 Secrets 加载", icon="✅")
    else:
        st.warning("请输入 API Key")

    st.markdown("---")
    st.markdown("""
    **使用方法：**
    1. 选择话题分类
    2. 点击「抓取新闻」
    3. 点击「生成帖子」
    4. 长按复制 → 粘贴到小红书/微信
    """)
    st.markdown("---")
    st.caption("Built for Sydney conveyancing & property solicitors 🇦🇺")


# ─── Topic selection ───
TOPICS = {
    "🏠 房产过户 Conveyancing": {
        "queries": [
            "Australia property conveyancing law changes 2026",
            "NSW stamp duty update news",
            "Sydney property settlement news",
        ],
        "angle": "房产过户、印花税、产权转让",
    },
    "📈 房市动态 Property Market": {
        "queries": [
            "Sydney property market news today",
            "Australia housing prices forecast 2026",
            "NSW property auction results",
        ],
        "angle": "悉尼房价走势、拍卖结果、市场预测",
    },
    "📜 遗嘱遗产 Wills & Estates": {
        "queries": [
            "Australia wills estate planning law news",
            "NSW probate inheritance dispute news",
            "Australia succession law update",
        ],
        "angle": "遗嘱规划、遗产分配、继承纠纷",
    },
    "🏗️ 信托架构 Trust Structures": {
        "queries": [
            "Australia family trust tax structure news 2026",
            "discretionary trust Australia tax update",
            "Australia property trust structure news",
        ],
        "angle": "家族信托、税务规划、资产保护架构",
    },
    "🌏 移民签证 Immigration": {
        "queries": [
            "Australia immigration visa policy update 2026",
            "Australia skilled visa news",
            "Australia investor visa property news",
        ],
        "angle": "签证政策变化、移民与购房、投资移民",
    },
}

st.markdown('<div class="section-label">📌 选择话题 Choose Topic</div>', unsafe_allow_html=True)
selected_topic = st.selectbox(
    "话题分类",
    options=list(TOPICS.keys()),
    label_visibility="collapsed",
)

# ─── Helper: call Anthropic with web search ───
def get_client():
    key = st.session_state.get("api_key", "")
    # Also check Streamlit Secrets (for deployed version)
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    if not key:
        st.error("⚠️ 请在左侧菜单输入你的 Anthropic API Key，或在 Streamlit Secrets 里配置")
        st.stop()
    return anthropic.Anthropic(api_key=key)


def fetch_news(client, topic_cfg):
    """Use Claude with web search to fetch and summarize latest news."""
    queries_text = "\n".join(f"- {q}" for q in topic_cfg["queries"])
    prompt = f"""You are a research assistant for a Sydney-based solicitor who specialises in conveyancing, property, wills, estates and trust structures, serving Chinese-speaking clients in Australia.

Search the web for the latest news on these topics:
{queries_text}

Return a JSON object (no markdown fences) with this structure:
{{
  "articles": [
    {{
      "headline": "English headline",
      "headline_cn": "中文标题",
      "summary": "2-3 sentence English summary of the key facts",
      "summary_cn": "2-3句中文摘要",
      "source": "source name",
      "relevance": "Why this matters for Chinese-speaking property buyers/families in Sydney"
    }}
  ]
}}

Find 3-5 of the most recent and relevant articles. Today's date is {datetime.now().strftime('%d %B %Y')}.
Focus on news from the last 2 weeks. If you can't find very recent news, get the most recent available.
Return ONLY the JSON object, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text from response blocks
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    # Clean and parse JSON
    full_text = full_text.strip()
    full_text = re.sub(r"^```json\s*", "", full_text)
    full_text = re.sub(r"\s*```$", "", full_text)

    try:
        return json.loads(full_text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        match = re.search(r"\{[\s\S]*\}", full_text)
        if match:
            return json.loads(match.group())
        return {"articles": [], "raw": full_text}


def generate_post(client, news_data, topic_cfg, platform):
    """Generate a social media post based on fetched news."""
    news_summary = json.dumps(news_data, ensure_ascii=False, indent=2)

    platform_instructions = {
        "小红书": """写一篇小红书风格的帖子。要求：
- 标题要有emoji，吸引眼球，用「」括起关键词
- 开头用一个幽默的小故事或段子引入话题（比如客户的搞笑经历、生活中的趣事类比）
- 语气亲切接地气，像朋友聊天，可以用"姐妹们"、"兄弟们"、"宝子们"开头
- 适当用emoji装饰但不要过度
- 中间穿插干货知识点，用简短的分点
- 结尾要有互动引导（点赞收藏评论）
- 最后加上 5-8 个相关hashtag标签
- 加上「📍悉尼 · 专业律师在线解答」
- 字数控制在 300-500 字
- 结尾引导私信咨询""",
        "微信": """写一篇微信公众号/朋友圈风格的帖子。要求：
- 标题专业但有趣，引发好奇心
- 开头用一个生动的故事或案例引入（可以虚构一个典型场景，加入幽默元素）
- 语气专业但不死板，偶尔来点幽默调侃
- 内容有深度，展示专业知识
- 段落分明，适合手机阅读
- 结尾有明确的行动号召
- 字数控制在 400-600 字
- 底部加联系方式引导""",
    }

    prompt = f"""你是一位在悉尼执业的华人律师，专精房产过户(conveyancing)、物业法、遗嘱遗产和信托架构。
你的目标读者是澳洲的华人社区。你的写作风格幽默风趣，善于用生活化的比喻和小故事来解释复杂的法律概念。

以下是最新抓取的相关新闻资讯：
{news_summary}

话题方向：{topic_cfg['angle']}

{platform_instructions[platform]}

重要提示：
1. 一定要加入幽默故事元素！可以是：
   - 一个虚构但真实感十足的客户故事（"上周有个客户来找我..."）
   - 把法律概念用做菜、打游戏、谈恋爱来类比
   - 自嘲律师生活的段子
2. 内容要基于上面的真实新闻，但用轻松的方式传达
3. 确保法律信息准确，但表达要接地气
4. 不要编造具体的法律条文数字，如果不确定就用"根据最新政策"这类表述

直接输出帖子内容，不要加任何前言或解释。"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


# ─── Main flow ───

# Initialize session state
if "news_data" not in st.session_state:
    st.session_state.news_data = None
if "posts" not in st.session_state:
    st.session_state.posts = {}

# Step 1: Fetch News
st.markdown('<div class="section-label">🔍 第一步：抓取新闻 Fetch News</div>', unsafe_allow_html=True)

if st.button("🔍 抓取最新新闻", use_container_width=True, type="primary"):
    client = get_client()
    topic_cfg = TOPICS[selected_topic]
    with st.spinner("🌐 正在搜索最新新闻... Searching latest news..."):
        try:
            news = fetch_news(client, topic_cfg)
            st.session_state.news_data = news
            st.session_state.posts = {}  # Reset posts when new news fetched
        except Exception as e:
            st.error(f"抓取失败: {e}")

# Display news
if st.session_state.news_data:
    articles = st.session_state.news_data.get("articles", [])
    if articles:
        st.markdown(f'<div class="news-card"><h4>📰 找到 {len(articles)} 条相关新闻</h4>', unsafe_allow_html=True)
        for i, article in enumerate(articles):
            hl = article.get("headline_cn", article.get("headline", ""))
            summary = article.get("summary_cn", article.get("summary", ""))
            source = article.get("source", "")
            st.markdown(f"**{i+1}. {hl}**")
            st.markdown(f"{summary}")
            if source:
                st.caption(f"来源: {source}")
            if i < len(articles) - 1:
                st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        raw = st.session_state.news_data.get("raw", "")
        if raw:
            st.info("获取到资讯但格式解析有误，已显示原始内容：")
            st.text(raw)
        else:
            st.warning("未找到相关新闻，请尝试其他话题")

    # Step 2: Generate Posts
    st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">✍️ 第二步：生成帖子 Generate Post</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        gen_xhs = st.button("📕 生成小红书帖", use_container_width=True, type="primary")
    with col2:
        gen_wx = st.button("💬 生成微信帖", use_container_width=True)

    if gen_xhs or gen_wx:
        client = get_client()
        topic_cfg = TOPICS[selected_topic]
        platform = "小红书" if gen_xhs else "微信"
        with st.spinner(f"✨ AI正在创作{platform}帖子..."):
            try:
                post = generate_post(client, st.session_state.news_data, topic_cfg, platform)
                st.session_state.posts[platform] = post
            except Exception as e:
                st.error(f"生成失败: {e}")

    # Display generated posts
    for platform, post in st.session_state.posts.items():
        st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)

        tag_class = "tag-xhs" if platform == "小红书" else "tag-wechat"
        icon = "📕" if platform == "小红书" else "💬"
        st.markdown(
            f'<span class="platform-tag {tag_class}">{icon} {platform}</span>',
            unsafe_allow_html=True,
        )

        st.markdown(f'<div class="content-card">{post}</div>', unsafe_allow_html=True)

        # Copy button using st.code (has built-in copy) + a cleaner text_area
        with st.expander(f"📋 点击复制 {platform} 内容", expanded=False):
            st.text_area(
                f"长按全选复制 (Long press to select & copy)",
                value=post,
                height=300,
                key=f"copy_{platform}",
                label_visibility="visible",
            )

        # Regenerate button
        if st.button(f"🔄 重新生成 {platform}", key=f"regen_{platform}"):
            client = get_client()
            topic_cfg = TOPICS[selected_topic]
            with st.spinner(f"✨ 重新创作中..."):
                try:
                    new_post = generate_post(client, st.session_state.news_data, topic_cfg, platform)
                    st.session_state.posts[platform] = new_post
                    st.rerun()
                except Exception as e:
                    st.error(f"生成失败: {e}")

# ─── Footer ───
st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)
st.caption("⚖️ 律师内容工厂 v1.0 — AI生成内容仅供参考，发布前请确认法律信息的准确性。")
