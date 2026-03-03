import asyncio
from ddgs import DDGS


class ArticleFetcher:

    @staticmethod
    async def list_articles(topics, keyword):
        unique_links = set()
        results = []

        with DDGS() as ddgs:
            for topic in topics:
                query = topic + " in " + keyword
                results_list = ddgs.text(query, max_results=1)

                for r in results_list:
                    link = r["href"]
                    if link not in unique_links:
                        unique_links.add(link)
                        results.append({
                            "topic": topic,
                            "link": link
                        })
                        break

        return results


async def main():
    topics = ["Artificial Intelligence", "Machine Learning", "Cyber Security"]
    keyword = "India"

    articles = await ArticleFetcher.list_articles(topics, keyword)

    print("\nFinal Results:")
    for article in articles:
        print(article)


if __name__ == "__main__":
    asyncio.run(main())