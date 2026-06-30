import asyncio
import os
import re
from urllib.parse import urljoin

import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode


LIST_PAGE_URL = "https://www.ebay.com/?templateId=template_170733d4-556d-11f1-b56d-55c90b8e6285&refinements=eyJrZXl3b3JkcyI6bnVsbCwiZXZlbnQiOnsiaWQiOiI2YTBmOTVhYzQ0ZmE2ZjAwMjBiYzUwY2YiLCJlYmF5Q3VyYXRlZEV2ZW50SWQiOiI2YTBmOTVhYzQ0ZmE2ZjAwMjBiYzUwY2YiLCJ0eXBlIjoiRFlOQU1JQyJ9LCJsZWdhY3lGaXRtZW50VG9rZW5zIjpbXSwic2VsZWN0ZWRMZWdhY3lDb250ZXh0IjpudWxsLCJpdGVtQ29uZGl0aW9ucyI6W10sImJ1eWluZ0Zvcm1hdHMiOltdLCJwcmVmZXJyZWRJdGVtTG9jYXRpb25zIjpudWxsLCJjYXRlZ29yeUNvbnN0cmFpbnQiOm51bGwsImF1dGhlbnRpY2l0eUd1YXJhbnRlZSI6bnVsbCwiYXV0aG9yaXplZFNlbGxlciI6bnVsbCwiY2hhcml0eU9ubHkiOm51bGwsImNvbXBsZXRlZEl0ZW1zT25seSI6bnVsbCwiZGVhbHMiOltdLCJlbmRUaW1lRnJvbSI6bnVsbCwiZnJlZVNoaXBwaW5nT25seSI6bnVsbCwibG9jYWxQaWNrdXBPbmx5IjpudWxsLCJsb3RzT25seSI6bnVsbCwicGF5bWVudE1ldGhvZCI6W10sInByaWNlUmFuZ2UiOm51bGwsInByb21vdGlvblNhbGUiOm51bGwsInJldHVybnNBY2NlcHRlZE9ubHkiOm51bGwsInNvbGRJdEl0ZW1zT25seSI6bnVsbCwic29ydCI6IkJlc3RNYXRjaCIsInJlZmluZW1lbnRPbmx5IjpmYWxzZSwicGFnaW5hdGlvbiI6eyJwYWdlTnVtYmVyIjoxLCJlbnRyaWVzUGVyUGFnZSI6NDh9LCJlYmF5U2VjdXJlQ2hlY2tvdXRMaXN0aW5nc09ubHkiOmZhbHNlLCJjZXJ0aWZpZWRSZWN5Y2xlZCI6bnVsbH0%253D"

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


# 상품명 가져올때 구조가 다를수있다. h1, span, title 이렇게
def pick_text(soup, selectors): 
    for selector in selectors:
        tag = soup.select_one(selector)

        if tag:
            text = clean_text(tag.get_text(" ", strip=True))

            if text:
                return text

    return None 


def extract_product_info(soup):
    info_tags = soup.select(
        "div.ux-layout-section__item, "
        "div.ux-labels-values, "
        "section.ux-layout-section"
    )

    info_list = []

    for tag in info_tags[:15]:
        text = clean_text(tag.get_text(" ", strip=True))

        if text and text not in info_list:
            info_list.append(text)

    if not info_list:
        return None

    return "\n".join(info_list)[:2000]


# def extract_shipping_fee(soup):
#     texts = list(soup.stripped_strings)

#     for text in texts:
#         lower_text = text.lower()

#         if "shipping" not in lower_text:
#             continue

#         if "thanks" in lower_text or "quick delivery" in lower_text:
#             continue

#         return clean_text(text)[:100]

#     return None
def extract_shipping_fee(product_info):
    if not product_info:
        return None

    lines = product_info.splitlines()

    for line in lines:
        text = clean_text(line)

        if not text:
            continue

        lower_text = text.lower()

        if text.startswith("배송:"):
            return text[:100]

        if lower_text.startswith("shipping:"):
            return text[:100]

    match = re.search(r"배송:[^\n\r]+", product_info)

    if match:
        return clean_text(match.group(0))[:100]

    return None

async def collect_product_urls(crawler):
    config = CrawlerRunConfig(
        wait_for="css:body",
        scan_full_page=True,
        scroll_delay=0.7,
        cache_mode=CacheMode.BYPASS,
    )

    result = await crawler.arun(
        url=LIST_PAGE_URL,
        config=config,
    )

    if not result.success:
        raise Exception(result.error_message)

    html = getattr(result, "cleaned_html", "") or getattr(result, "html", "")
    soup = BeautifulSoup(html, "html.parser")

    product_urls = []

    for a_tag in soup.select('a[href*="/itm/"]'):
        href = a_tag.get("href")

        if not href:
            continue

        full_url = urljoin("https://www.ebay.com", href)


        # 이베이에는 추적 파라미터가 많이 붙는다 그대로 저장하면
        # 같은상품인데 URL이 다르게 인식. 그래서 ID기준으로 통일(중복저장 방지)
        match = re.search(r"/itm/(?:[^/?#]+/)?(\d+)", full_url)


        if not match:
            continue

        item_id = match.group(1)
        product_url = f"https://www.ebay.com/itm/{item_id}"

        # 목록에는 상품이미지링크나 상품제목링크나 같은상품링크가 여러곳에 있을수있다
        # 둘다 같은상세페이지로 가게함 (중복방지))
        if product_url not in product_urls:
            product_urls.append(product_url)

        if len(product_urls) >= LIMIT:
            break

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

    html = getattr(result, "cleaned_html", "") or getattr(result, "html", "")
    soup = BeautifulSoup(html, "html.parser")

    name = pick_text(
        soup,
        [
            "h1.x-item-title__mainTitle span",
            "h1 span",
            "h1",
            "title",
        ],
    )

    sale_price = pick_text(
        soup,
        [
            "div.x-price-primary span",
            "span[itemprop='price']",
            ".x-price-primary",
        ],
    )

    original_price = pick_text(
        soup,
        [
            ".ux-textspans--STRIKETHROUGH",
            ".x-price-original",
        ],
    )

    product_info = extract_product_info(soup)
    shipping_fee = extract_shipping_fee(product_info)

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
        ("ebay", "eBay", "https://www.ebay.com"),
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