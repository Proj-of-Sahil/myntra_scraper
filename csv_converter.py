from bs4 import BeautifulSoup
import csv

with open("./output2.html") as file:
    html = file.read()

soup = BeautifulSoup(html, "html.parser")

# Open the CSV file in write mode
with open("products_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Writing the headers
    writer.writerow(
        ["URL", "Brand", "Title", "Price", "Discount", "Rating", "Number of Reviews"]
    )

    for li in soup.find_all("li", class_="product-base"):
        url_element = li.find("a", {"data-refreshpage": "true"})
        url = url_element["href"] if url_element else "NA"

        brand_element = li.find("h3", class_="product-brand")
        brand = brand_element.text if brand_element else "NA"

        title_element = li.find("h4", class_="product-product")
        title = title_element.text if title_element else "NA"

        price_element = li.find("span", class_="product-discountedPrice")
        price = price_element.text if price_element else "NA"

        discount_element = li.find("span", class_="product-discountPercentage")
        discount = discount_element.text if discount_element else "NA"

        rating_container = li.find("div", class_="product-ratingsContainer")
        rating = (
            rating_container.find("span").text
            if rating_container and rating_container.find("span")
            else "NA"
        )

        reviews_element = li.find("div", class_="product-ratingsCount")
        reviews = (
            reviews_element.text.split("|")[-1].strip()
            if reviews_element
            else "NA"
        )

        # Writing the product data to the CSV file
        writer.writerow([url, brand, title, price.strip(), discount, rating, reviews])
