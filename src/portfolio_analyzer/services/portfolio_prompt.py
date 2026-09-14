def build_portfolio_analysis_prompt(
        portfolio_context: str,
        user_prompt: str,
) -> str:
    return (
        "Here's the user's portfolio:\n\n"
        f"{portfolio_context}\n\n"
        "User's question:\n"
        f"{user_prompt}\n\n"
        "Analyse the portfolio and answer the user's question.\n\n"
        "The response should be structured as follows:\n\n"
        "summary → concise overall assessment\n"
        "diversification → concentration and diversification\n"
        "risks → specific risks identified in the portfolio\n"
        "recommendations → actionable suggestions"
    )


if __name__ == "__main__":
    portfolio_context = "AAPL: 10 shares\nNVDA: 2 shares"

    user_prompt = "Is my portfolio diversified?"

    result = build_portfolio_analysis_prompt(portfolio_context, user_prompt)

    print(result)
