import asyncio
import os
import re
from urllib.parse import urljoin

import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode


LIST_PAGE_URL = "https://www.amazon.com/s?k=gaming+action+figures&i=toys-and-games-intl-ship&language=ko&_encoding=UTF8&pf_rd_p=39fc32bd-755e-448d-add5-8e4518ce2470&pf_rd_r=HD9P4RFVC2M0JMY0QJWP&ref=cct_cg_purimil_4c1"
LIMIT = 30


def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "datriss"),
        user=os.getenv("DB_USER", "hongmun-il"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def clean_text(text):
    if not text:
        return None

    return re.sub(r"\s+", " ", text).strip()


def pick_text(soup, selectors):
    for selector in selectors:
        tag = soup.select_one(selector)

        if tag:
            text = clean_text(tag.get_text(" ", strip=True))

            if text:
                return text

    return None


def extract_product_info(soup):
    info_list = []

    for tag in soup.select("#feature-bullets li span.a-list-item"):
        text = clean_text(tag.get_text(" ", strip=True))

        if text and text not in info_list:
            info_list.append(text)

    if not info_list:
        for tag in soup.select("#productOverview_feature_div tr"):
            text = clean_text(tag.get_text(" ", strip=True))

            if text and text not in info_list:
                info_list.append(text)

    if not info_list:
        return None

    return "\n".join(info_list)[:2000]

def extract_shipping_fee(soup):
    copied_soup = BeautifulSoup(str(soup), "html.parser")

    remove_selectors = [
        "#reviewsMedley",
        "#customerReviews",
        "#cm-cr-dp-review-list",
        "#ask_feature_div",
        "#customer-reviews_feature_div",
        "script",
        "style",
        "noscript",
    ]

    for selector in remove_selectors:
        for tag in copied_soup.select(selector):
            tag.decompose()

    page_text = clean_text(copied_soup.get_text(" ", strip=True))

    if not page_text:
        return None

    patterns = [
        r"아마존\s*글로벌\s*배송\s*KRW\s*[\d,]+",
        r"KRW\s*[\d,]+\s*배송",
        r"무료\s*(?:해외\s*)?배송",
        r"FREE\s+delivery[^.]{0,80}",
        r"\$[\d,.]+\s*(?:shipping|delivery)",
    ]

    for pattern in patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)

        if match:
            return clean_text(match.group(0))[:120]

    return None

async def collect_product_urls(crawler):
    config = CrawlerRunConfig(
        wait_for="css:body",
        scan_full_page=True,
        scroll_delay=1,
        delay_before_return_html=3,
        cache_mode=CacheMode.BYPASS,
    )

    result = await crawler.arun(
        url=LIST_PAGE_URL,
        config=config,
    )

    if not result.success:
        raise Exception(result.error_message)

    html = getattr(result, "html", "") or getattr(result, "cleaned_html", "")

    with open("amazon_list_debug.html", "w", encoding="utf-8") as file:
        file.write(html)

    soup = BeautifulSoup(html, "html.parser")

    title = pick_text(soup, ["title"])
    print("목록 페이지 title:", title)

    html_lower = html.lower()

    if "robot check" in html_lower or "captcha" in html_lower:
        print("Amazon 봇 확인 페이지가 뜬 것으로 보입니다.")
        print("amazon_list_debug.html 파일을 열어서 확인해보세요.")
        return []

    product_urls = []

    selectors = [
        'div[data-component-type="s-search-result"] h2 a[href]',
        'a.a-link-normal.s-no-outline[href]',
        'a[href*="/dp/"]',
        'a[href*="/gp/product/"]',
    ]

    for selector in selectors:
        for a_tag in soup.select(selector):
            href = a_tag.get("href")

            if not href:
                continue

            full_url = urljoin("https://www.amazon.com", href)

            match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", full_url)

            if not match:
                continue

            asin = match.group(1)
            product_url = f"https://www.amazon.com/dp/{asin}"

            if product_url not in product_urls:
                product_urls.append(product_url)

            if len(product_urls) >= LIMIT:
                break

        if len(product_urls) >= LIMIT:
            break

    print(f"추출된 Amazon 상품 URL 후보 개수: {len(product_urls)}")

    return product_urls

async def crawl_detail(crawler, product_url):
    config = CrawlerRunConfig(
        wait_for="css:body",
        delay_before_return_html=2,
        cache_mode=CacheMode.BYPASS,
    )

    result = await crawler.arun(
        url=product_url,
        config=config,
    )

    if not result.success:
        raise Exception(result.error_message)

    html = getattr(result, "html", "") or getattr(result, "cleaned_html", "")
    soup = BeautifulSoup(html, "html.parser")

    name = pick_text(
    soup,
    [
        "#productTitle",
        "span#productTitle",
        "h1 span",
        "title",
    ],
)

    sale_price = pick_text(
    soup,
    [
        "#corePrice_feature_div span.a-price span.a-offscreen",
        "span.a-price span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
    ],
)

    original_price = pick_text(
    soup,
    [
        "span.a-price.a-text-price span.a-offscreen",
        ".basisPrice span.a-offscreen",
    ],
)

    product_info = extract_product_info(soup)
    shipping_fee = extract_shipping_fee(soup)

    return {
        "name": name,
        "rating": None,
        "original_price": original_price,
        "sale_price": sale_price,
        "shipping_fee": shipping_fee,
        "product_info": product_info,
        "product_url": product_url,
    }


def get_platform_id(cursor):
    cursor.execute(
        """
        INSERT INTO platforms (code, name, base_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (code)
        DO UPDATE SET
            name = EXCLUDED.name,
            base_url = EXCLUDED.base_url,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """,
        ("amazon", "amazon", "https://www.amazon.com"),
    )

    return cursor.fetchone()[0]


def save_product(cursor, platform_id, product):
    cursor.execute(
        """
        INSERT INTO products (
            platform_id,
            name,
            rating,
            original_price,
            sale_price,
            shipping_fee,
            product_info,
            product_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_url)
        DO UPDATE SET
            name = EXCLUDED.name,
            rating = EXCLUDED.rating,
            original_price = EXCLUDED.original_price,
            sale_price = EXCLUDED.sale_price,
            shipping_fee = EXCLUDED.shipping_fee,
            product_info = EXCLUDED.product_info,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            platform_id,
            product["name"],
            product["rating"],
            product["original_price"],
            product["sale_price"],
            product["shipping_fee"],
            product["product_info"],
            product["product_url"],
        ),
    )


async def main():
    load_dotenv()

    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
    )

    conn = connect_db()

    with conn:
        with conn.cursor() as cursor:
            platform_id = get_platform_id(cursor)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            product_urls = await collect_product_urls(crawler)
        except Exception as error:
            print("목록 페이지 크롤링 실패:", error)
            conn.close()
            return

        print(f"수집된 상품 URL 개수: {len(product_urls)}")

        for index, product_url in enumerate(product_urls, start=1):
            try:
                product = await crawl_detail(crawler, product_url)

                with conn:
                    with conn.cursor() as cursor:
                        save_product(cursor, platform_id, product)

                print(f"{index}. 저장 완료: {product['name']}")

                await asyncio.sleep(1)

            except Exception as error:
                print(f"{index}. 상세 페이지 실패: {product_url}")
                print(error)

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())