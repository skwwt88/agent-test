import requests
from langchain_core.tools import tool


@tool
def get_my_ip_location() -> str:
    """获取当前公网 IP 和大致地理位置。"""
    providers = [
        "https://ipapi.co/json/",
        "https://ipwho.is/",
        "https://ipinfo.io/json",
    ]

    data = None
    last_error = ""
    for url in providers:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            candidate = response.json()
            if isinstance(candidate, dict):
                data = candidate
                break
        except requests.RequestException as exc:
            last_error = str(exc)

    if not data:
        return f"查询 IP 失败：{last_error or '所有服务暂时不可用'}"

    ip = data.get("ip", data.get("query", "unknown"))
    city = data.get("city", "unknown")
    region = data.get("region", data.get("regionName", "unknown"))
    country = data.get("country_name", data.get("country", "unknown"))
    org = data.get("org", data.get("isp", data.get("org_name", "unknown")))
    timezone = data.get("timezone", data.get("time_zone", "unknown"))

    return (
        "当前网络信息：\n"
        f"- IP: {ip}\n"
        f"- 位置: {city}, {region}, {country}\n"
        f"- 时区: {timezone}\n"
        f"- 运营商/组织: {org}"
    )


@tool
def get_weather_by_city(city: str) -> str:
    """按城市查询当前天气。输入参数为城市名，例如: Beijing, Shanghai, Tokyo。"""
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh", "format": "json"},
            timeout=10,
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()
    except requests.RequestException as exc:
        return f"城市查询失败：{exc}"

    results = geo_data.get("results") or []
    if not results:
        return f"未找到城市：{city}"

    target = results[0]
    lat = target.get("latitude")
    lon = target.get("longitude")
    resolved_city = target.get("name", city)
    country = target.get("country", "")

    try:
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
    except requests.RequestException as exc:
        return f"天气查询失败：{exc}"

    current = weather_data.get("current", {})
    if not current:
        return f"未获取到 {resolved_city} 的实时天气。"

    weather_code = current.get("weather_code", "unknown")
    return (
        f"{resolved_city} {country} 当前天气：\n"
        f"- 温度: {current.get('temperature_2m', 'unknown')}°C\n"
        f"- 体感温度: {current.get('apparent_temperature', 'unknown')}°C\n"
        f"- 湿度: {current.get('relative_humidity_2m', 'unknown')}%\n"
        f"- 风速: {current.get('wind_speed_10m', 'unknown')} km/h\n"
        f"- 天气代码: {weather_code} (可让助手解释代码含义)"
    )
