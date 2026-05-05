import duckduckgo_search
import httpx

async def gather_destination_info(destination: str) -> dict:
    """Gathers destination intelligence from DuckDuckGo and a mock API.

    Args:
        destination: The destination string.

    Returns:
        A dictionary containing destination intelligence.
    """

    try:
        # Use DuckDuckGo Search API
        ddg_results = duckduckgo_search.DDGS().text(destination, max_results=3)
        duckduckgo_info = []
        for result in ddg_results:
            duckduckgo_info.append(result.url)

        # Mock API call (replace with actual API integration)
        async with httpx.AsyncClient() as client:
            api_url = f"https://api.example.com/destination/{destination}"
            api_response = await client.get(api_url)
            if api_response.status_code == 200:
                api_data = api_response.json()
            else:
                api_data = {"error": f"API request failed with status code: {api_response.status_code}"}

        intelligence = {
            "duckduckgo": duckduckgo_info,
            "api": api_data,
        }

        return intelligence

    except Exception as e:
        return {"error": str(e)}
