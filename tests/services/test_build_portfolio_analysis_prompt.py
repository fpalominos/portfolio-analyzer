from portfolio_analyzer.services.portfolio_prompt import build_portfolio_analysis_prompt
from textwrap import dedent


def test_build_portfolio_analysis_prompt_includes_portfolio_and_user_question():
    expected_prompt = dedent("""\
        Here's the user's portfolio:
        
        AAPL: 10 shares
        NVDA: 2 shares
        
        User's question:
        Is my portfolio diversified?
        
        Analyse the portfolio and answer the user's question""")

    portfolio_context = "AAPL: 10 shares\nNVDA: 2 shares"
    user_question = "Is my portfolio diversified?"

    actual_prompt = build_portfolio_analysis_prompt(portfolio_context, user_question)

    assert actual_prompt == expected_prompt
