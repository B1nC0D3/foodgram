from posts.models import Ingredient
import csv

def run():
    with open('ingredients.csv') as file:
        reader = csv.reader(file)
        print(reader)

        for row in reader:
            product = Ingredient(
                name=row[0],
                measurement_unit=row[-1],
            )
            product.save()