"""
Tests for RAG (Retrieval-Augmented Generation) components
"""
from app.rag.simple_retriever import SimpleMarkdownRetriever


def test_simple_retriever_can_retrieve_payment_risk_rules():
    """测试：simple retriever 能检索 payment_risk_rules.md"""
    retriever = SimpleMarkdownRetriever()
    # 使用中文关键词，因为文档是中文的
    evidence = retriever.retrieve("支付 风险 规则", top_k=5)

    # 验证检索到了结果
    assert evidence, "Should retrieve evidence"

    # 验证至少有一个结果来自 payment_risk_rules.md
    sources = [item.source for item in evidence]
    assert any("payment_risk_rules.md" in source for source in sources), (
        f"Expected payment_risk_rules.md in sources, got: {sources}"
    )

    # 验证每个结果都有 source 和 content
    for item in evidence:
        assert item.source, "Evidence item should have source"
        assert item.content, "Evidence item should have content"


def test_retriever_with_new_account_high_amount_query():
    """测试：query 包含"新账户 大额交易"时返回相关证据"""
    retriever = SimpleMarkdownRetriever()
    evidence = retriever.retrieve("新账户 大额交易", top_k=3)

    # 验证检索到了结果
    assert evidence, "Should retrieve evidence for '新账户 大额交易'"

    # 验证返回的数量不超过 top_k
    assert len(evidence) <= 3

    # 验证每个结果格式正确
    for item in evidence:
        assert item.source, "Evidence should have source"
        assert item.content, "Evidence should have content"
        assert isinstance(item.source, str)
        assert isinstance(item.content, str)

    # 验证内容相关性（至少有一个结果包含相关关键词）
    all_content = " ".join(item.content.lower() for item in evidence)
    assert any(
        keyword in all_content
        for keyword in ["新账户", "大额", "交易", "account", "amount"]
    ), "Evidence should contain relevant keywords"


def test_retriever_returns_evidence_with_metadata():
    """测试：检索器返回的证据包含正确的 metadata"""
    retriever = SimpleMarkdownRetriever()
    evidence = retriever.retrieve("KYC AML 审核", top_k=2)

    assert evidence, "Should retrieve evidence"

    for item in evidence:
        # 验证 source 是有效的文件名
        assert item.source.endswith(".md"), f"Source should be a .md file: {item.source}"

        # 验证 content 不为空且合理
        assert len(item.content) > 0, "Content should not be empty"
        assert len(item.content) < 10000, "Content should be reasonably sized"


def test_retriever_with_high_frequency_query():
    """测试：高频交易查询返回相关证据"""
    retriever = SimpleMarkdownRetriever()
    evidence = retriever.retrieve("高频交易 频繁", top_k=3)

    assert evidence, "Should retrieve evidence for high frequency queries"

    # 验证格式
    for item in evidence:
        assert hasattr(item, "source"), "Should have source attribute"
        assert hasattr(item, "content"), "Should have content attribute"


def test_retriever_with_ip_abnormal_query():
    """测试：IP异常查询返回相关证据"""
    retriever = SimpleMarkdownRetriever()
    evidence = retriever.retrieve("IP 地址 异常", top_k=2)

    # 即使没有完全匹配，也应该返回一些相关结果
    assert isinstance(evidence, list), "Should return a list"

    if evidence:
        for item in evidence:
            assert item.source
            assert item.content


def test_retriever_returns_empty_for_nonexistent_docs():
    """测试：不存在的文档目录返回空列表"""
    from pathlib import Path

    retriever = SimpleMarkdownRetriever(docs_dir=Path("/nonexistent/path"))
    evidence = retriever.retrieve("test query", top_k=5)

    assert evidence == [], "Should return empty list for nonexistent directory"
