from posts.models import Ingredients
import csv

def run():
    with open('ingredients.csv') as file:
        reader = csv.reader(file)
        print(reader)

        for row in reader:
            product = Ingredients(
                name=row[0],
                measurement_unit=row[-1],
            )
            product.save()