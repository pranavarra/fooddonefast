import json
import itertools
import google.generativeai as genai
import textwrap

# Load data from JSON file
with open('food_items.json', 'r') as foods_file:
    data = json.load(foods_file)

# Extract food data from loaded JSON
food_data = data["foods"]

# Function to filter foods based on dietary preferences and allergies

class UserData:
    def __init__(self, weight, height, age, gender, activity_level, goal, dietary_preference, allergies_input = "", meals=4):
        
    #allergies_input = input("Do you have any allergies? (Separate multiple allergies with commas, leave blank if none): ")
        allergies = [allergy.strip() for allergy in allergies_input.split(',') if allergy.strip()]
    # Convert lbs to kg and inches to cm
        self.weight_kg = weight * 0.453592
        self.height_cm = height * 2.54

        filtered_food_data = self.filter_foods(dietary_preference, allergies)

        # Calculate calorie intake and other nutritional values
        calorie_intake, protein, fats, carbs, fiber, calspermeal = self.calculate_calorie_intake(self.weight_kg, self.height_cm, age, gender, activity_level, goal, meals)

        # Initialize output string
        output_string = ""

        # Append the user's daily calorie intake and nutritional values to the output string
        output_string += f"\nYour daily calorie intake: {round(calorie_intake, 2)} calories\n"
        output_string += f"Protein: {round(protein, 2)} grams\n"
        output_string += f"Fats: {round(fats, 2)} grams\n"
        output_string += f"Carbohydrates: {round(carbs, 2)} grams\n"
        output_string += f"Fiber: {round(fiber, 2)} grams\n\n"

        # Meal structure based on the number of meals per day
        meal_structure = {
            2: ['Lunch', 'Dinner'],
            3: ['Breakfast', 'Lunch', 'Dinner'],
            4: ['Breakfast', 'Lunch', 'Snack', 'Dinner']
        }

        # Select combination of foods (with filtered_food_data) that sum up to approximately calspermeal for each meal
        selected_foods_per_meal = []
        remaining_food_data = filtered_food_data.copy()  # Use filtered_food_data instead of food_data

        if meals in meal_structure:
            for meal in meal_structure[meals]:
                found_combination = False
                for r in range(1, len(remaining_food_data) + 1):
                    for combination in itertools.combinations(remaining_food_data, r):
                        total_calories = sum(food['calories'] for food in combination)
                        if abs(total_calories - calspermeal) <= 200:  # Allow a difference of 200 calories
                            selected_foods_per_meal.append((meal, list(combination)))
                            # Remove selected foods from the remaining food data
                            remaining_food_data = [food for food in remaining_food_data if food not in combination]
                            found_combination = True
                            break
                    if found_combination:
                        break
        else:
            output_string += "Invalid number of meals per day.\n"

        # Append selected foods for each meal to the output string
        output_string += "\nSelected foods for each meal:\n"
        self.groceries = []
        for i, (meal, foods) in enumerate(selected_foods_per_meal):
            
            output_string += f"\nMeal {i + 1} ( {meal} ):\n"
            for food in foods:
                self.groceries.append(food)
                food_name = food.get('food_name', 'Unknown Food')
                food_calories = food.get('calories', 'Unknown')
                output_string += f"{food_name}: {round(food_calories, 2)} calories\n"  # Rounding food calories to two decimal places

        # Print or save the output string
        print(output_string)

        

        # Save the output string to a file
        with open('output.txt', 'w') as file:
            file.write(output_string)


        def to_markdown(text):
            text = text.replace('•', '  *')
            return textwrap.indent(text, '> \n', predicate=lambda _: True)

        genai.configure(api_key='AIzaSyD-POzLi-u0Fpn52fqpVN7I37YCHxpIu0w')

        model = genai.GenerativeModel('gemini-pro')
        prompt = """
        What recipes can I make with the following ingredients. Make long list. only type recipes.
        type how to make it, what ingredients are needed to make it, and the name of the dish, and the final calories: " + output_string
        """
        prompt += "\n".join(output_string)

        response = model.generate_content(prompt)

        webappdata = ""

        lines=[]
        # Append the user's daily calorie intake and nutritional values to the webappdata string
        lines.append(f"\nYour daily calorie intake: {round(calorie_intake, 2)} calories\n")
        lines.append(f"Protein: {round(protein, 2)} grams\n")
        lines.append(f"Fats: {round(fats, 2)} grams\n")
        lines.append(f"Carbohydrates: {round(carbs, 2)} grams\n")
        lines.append(f"Fiber: {round(fiber, 2)} grams\n\n")
        lines.append(-1)
        foods_str = ""
        # Append selected foods for each meal to the webappdata string
        foods_str += "\nSelected foods for each meal:\n"
        for i, (meal, foods) in enumerate(selected_foods_per_meal):
            webappdata += f"\nMeal {i + 1} ( {meal} ):\n"
            for food in foods:
                food_name = food.get('food_name', 'Unknown Food')
                food_calories = food.get('calories', 'Unknown')
                lines.append(f"{food_name}: {round(food_calories, 2)} calories\n")  # Rounding food calories to two decimal places

        recipes = ""
        lines.append(-1)
        
        # Append the Geminai output to the webappdata string
        webappdata += "\nGeminai Output:\n"
        recipes = to_markdown(response.text)  # Assuming response.text contains the generated content
        
        # Save the webappdata to a file or send it to the web application
        with open('webappdata.txt', 'w') as file:
            file.write(webappdata)
        num_chars = len(webappdata)
        split_index_1 = num_chars // 3
        split_index_2 = 2 * (num_chars // 3)

        part1 = webappdata[:split_index_1]
        part2 = webappdata[split_index_1:split_index_2]
        part3 = webappdata[split_index_2:]

        recipes = self.parsedata(recipes)

        lines.append(recipes)
        #lines += [part1, part2, part3]
        self.userdata = lines
        pass

    def parsedata(self, data):
        x = data.replace("> >","<br><br>")
        
        y = x.replace(">","<br>")
        return y
    
    def get_groceries(self):
        print(self.groceries)
        #with open('temp.json', 'w') as writeF:
        #    json.dump(self.groceries, writeF)
        return self.groceries

    def get_user_data(self):
        return self.userdata
    def filter_foods(self, dietary_preference, allergies):
        filtered_food_data = []
        for food in food_data:
            if dietary_preference == 'vegan' and 'non-vegetarian' in food['category']:
                continue
            if dietary_preference == 'vegetarian' and 'non-vegetarian' in food['category']:
                continue
            if any(allergy in food['allergies'] for allergy in allergies):
                continue
            filtered_food_data.append(food)
        return filtered_food_data

    # Function to calculate calorie intake
    def calculate_calorie_intake(self, weight, height, age, gender, activity_level, goal, meals):
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        elif gender.lower() == 'female':
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        else:
            return "Invalid gender. Please enter 'male' or 'female'."

        activity_multipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55, 'very active': 1.725, 'extra active': 1.9}
        activity_multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        calorie_intake = bmr * activity_multiplier

        if goal.lower() == 'gain':
            calorie_intake += 500  
        elif goal.lower() == 'lose':
            calorie_intake -= 500  

        protein = (calorie_intake * 0.15) / 4  
        fats = (calorie_intake * 0.25) / 9  
        carbs = (calorie_intake - (protein * 4) - (fats * 9)) / 4 
        fiber = 25 if gender.lower() == 'female' else 38
        calspermeal = calorie_intake / meals

        return calorie_intake, protein, fats, carbs, fiber, calspermeal
    
    