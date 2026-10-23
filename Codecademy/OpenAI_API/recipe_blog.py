from openai import OpenAI

# Initialize client (uses OPENAI_API_KEY from environment)
client = OpenAI()

user_profile = {
  "dietary_restrictions": "gluten-free, keto",
  "cuisine_preferences": "japanese, mexican, american",
  "ingredients_available": "rice, tuna, bread, sugar, salt, oil, onion, tomato, lettuce, tortilla, refried beans, spaguetti, flour, Lizano sauce"
}

system_prompt = {
  "role": "system",
  "content": "Generate HTML code for a recipe blog that takes into account specific dietary restrictions, chosen cuisine type, and a provided list of ingredients. Return only valid HTML. Do not include markdown, explanations, or code fences."
}

user_content1 = (
    f"I want to create a recipe blog post. "
    f"Respect my dietary restrictions: {user_profile['dietary_restrictions']}. "
    f"My cuisine preferences include: {user_profile['cuisine_preferences']}. "
    f"The ingredients I have available are: {user_profile['ingredients_available']}."
)

user_content2 = "Please provide a blog post with a title, description, ingredients, and instructions. Format the ingredients and instructions as follows: Ingredients should be bulleted, and instructions should be numbered."

user_content3 = "The recipe must use only the listed ingredients and should result in a single blog post with instructions not exceeding six steps."

user_prompt = {
  "role": "user",
  "content": user_content1 + "\n" + user_content2 + "\n" + user_content3
}

response = client.chat.completions.create(
  model="gpt-4o-mini",
  temperature=0,
  max_tokens=1000,
  messages=[system_prompt, user_prompt] # pyright: ignore[reportArgumentType]
)

html_content = response.choices[0].message.content

with open("recipe_blog.html", "w", encoding="utf-8") as file:
    file.write(html_content) # type: ignore

print("HTML file created successfully: recipe_blog.html")