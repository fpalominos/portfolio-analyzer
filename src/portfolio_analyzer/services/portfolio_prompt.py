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
        "recommendations → actionable suggestions\n\n"
        "Accuracy and data integrity:\n"
        "- Never invent stock prices, holdings, allocation percentages, "
        "or other financial figures.\n"
        "- Use the supplied portfolio context and tool results as the "
        "source of truth for portfolio-specific facts.\n"
        "- If required data is unavailable or a tool returns an error, "
        "explicitly explain what could not be retrieved and how this "
        "limits the analysis.\n"
        "- Never claim to have calculated a value unless the necessary "
        "data is available and the calculation has been performed.\n"
        "- Clearly distinguish facts derived from portfolio data and "
        "calculations from general financial commentary, assumptions, "
        "and recommendations.\n"
        "- If only partial data is available, analyse what can be "
        "supported and clearly state the limitations.\n"
    )


if __name__ == "__main__":
    portfolio_context = "AAPL: 10 shares\nNVDA: 2 shares"

    user_prompt = "Is my portfolio diversified?"

    result = build_portfolio_analysis_prompt(portfolio_context, user_prompt)

    print(result)
