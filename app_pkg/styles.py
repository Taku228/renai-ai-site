APP_CSS = """
<style>
.block-container { padding-top: 6.5rem; padding-bottom: 2rem; max-width: 860px; }
@media (max-width: 640px) {
  .block-container { padding-top: 8.2rem; padding-left: 0.7rem; padding-right: 0.7rem; padding-bottom: 1.5rem; }
}
.main-card,.section-card,.reply-card,.plan-card,.plan-card-highlight,.memory-box,.upgrade-box,.judgement-box,.paywall-box {
  border-radius: 16px; padding: 1rem; margin-bottom: 1rem; line-height: 1.7; color: #0f172a !important;
}
.main-card *,.section-card *,.reply-card *,.plan-card *,.plan-card-highlight *,.memory-box *,.upgrade-box *,.judgement-box *,.paywall-box * { color: #0f172a !important; }
.main-card,.section-card,.plan-card,.reply-card { background:#fff; border:1px solid #e5e7eb; }
.reply-card { border-color:#dbeafe; }
.plan-card-highlight { background:#eff6ff; border:1px solid #3b82f6; }
.memory-box { background:#f8fafc; border:1px solid #e2e8f0; }
.upgrade-box { background:#fff7ed; border:1px solid #fb923c; color:#7c2d12 !important; }
.upgrade-box * { color:#7c2d12 !important; }
.judgement-box { background:#ecfeff; border:1px solid #67e8f9; }
.paywall-box { background:#fef3c7; border:1px solid #f59e0b; }
.app-title { font-size:1.72rem; font-weight:800; margin-bottom:0.18rem; line-height:1.3; }
.app-subtitle { color:#475569 !important; font-size:0.98rem; line-height:1.6; margin-bottom:0.18rem; }
.result-title,.plan-title { font-weight:800; }
.result-title { font-size:1.16rem; margin-bottom:0.6rem; }
.plan-title { font-size:1rem; margin-bottom:0.35rem; }
.small-note,.reply-meta,.copy-help { color:#475569 !important; font-size:0.95rem; }
.badge { display:inline-block; font-size:0.85rem; font-weight:700; padding:0.25rem 0.55rem; border-radius:999px; background:#eff6ff; color:#1d4ed8 !important; border:1px solid #bfdbfe; margin-bottom:0.55rem; }
.meter-row { margin:0.25rem 0; }
hr.soft { border:none; border-top:1px solid #e5e7eb; margin:0.95rem 0 0.8rem 0; }
.stButton > button { border-radius:12px; padding:0.6rem 1rem; font-weight:700; min-height:48px; font-size:0.98rem; }
div[data-testid="stTextArea"] textarea { border-radius:12px; font-size:16px !important; line-height:1.6; }
div[data-testid="stSelectbox"] > div { border-radius:12px; }
@media (max-width: 640px) {
  .main-card,.section-card,.reply-card,.plan-card,.plan-card-highlight,.memory-box,.upgrade-box,.judgement-box,.paywall-box { padding:0.9rem; font-size:0.95rem; }
  .app-title { font-size:1.35rem; }
  .app-subtitle { font-size:0.93rem; }
  .result-title { font-size:1.05rem; }
  .small-note { font-size:0.9rem; }
  .stButton > button { min-height:50px; font-size:1rem; }
}
header, footer { visibility:hidden; }
</style>
"""
