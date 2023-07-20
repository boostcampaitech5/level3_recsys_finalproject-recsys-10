from Ingredient_Based_Recipe_RecSys import get_recipe_by_ingredient_based_recsys

preference_recipe = ['돼지고기', '베이컨', '소금', '마늘', '닭가슴살', '양파', '간장', '설탕', '대파']
Rec_recipe = get_recipe_by_ingredient_based_recsys(preference_recipe)

print(Rec_recipe)



