from posts.models import Products
import csv

def run():
    with open('ingredients.csv') as file:
        reader = csv.reader(file)
        print(reader)

        for row in reader:
            product = Products(
                name=row[0],
                measure=row[-1],
            )
            product.save()