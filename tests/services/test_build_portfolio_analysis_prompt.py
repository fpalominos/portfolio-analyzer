from textwrap import dedent

from portfolio_analyzer.services.portfolio_prompt import (
    build_portfolio_analysis_prompt,
)


def test_build_prompt_includes_portfolio_context_and_user_question():
    portfolio_context = "NVDA: 10 shares, current price $150"
    user_prompt = "Analyse my portfolio risk."

    result = build_portfolio_analysis_prompt(
        portfolio_context=portfolio_context,
        user_prompt=user_prompt,
    )

    assert portfolio_context in result
    assert user_prompt in result


def test_build_prompt_includes_accuracy_instructions():
    result = build_portfolio_analysis_prompt(
        portfolio_context="NVDA: 10 shares",
        user_prompt="Analyse my portfolio.",
    )

    assert "Never invent stock prices" in result
    assert "source of truth" in result
    assert "explicitly explain what could not be retrieved" in result
    assert "Clearly distinguish facts" in result
    assert "partial data is available" in result


def test_build_portfolio_analysis_prompt_includes_portfolio_and_user_question():
    expected_prompt = dedent("""\
        Here's the user's portfolio:

        AAPL: 10 shares
        NVDA: 2 shares

        User's question:
        Is my portfolio diversified?

        Analyse the portfolio and answer the user's question.

        The response should be structured as follows:

        summary → concise overall assessment
        diversification → concentration and diversification
        risks → specific risks identified in the portfolio
        recommendations → actionable suggestions

        Accuracy and data integrity:
        - Never invent stock prices, holdings, allocation percentages, or other financial figures.
        - Use the supplied portfolio context and tool results as the source of truth for portfolio-specific facts.
        - If required data is unavailable or a tool returns an error, explicitly explain what could not be retrieved and how this limits the analysis.
        - Never claim to have calculated a value unless the necessary data is available and the calculation has been performed.
        - Clearly distinguish facts derived from portfolio data and calculations from general financial commentary, assumptions, and recommendations.
        - If only partial data is available, analyse what can be supported and clearly state the limitations.
    """)

    portfolio_context = "AAPL: 10 shares\nNVDA: 2 shares"
    user_question = "Is my portfolio diversified?"

    actual_prompt = build_portfolio_analysis_prompt(portfolio_context=portfolio_context, user_prompt=user_question)

    assert actual_prompt == expected_prompt
