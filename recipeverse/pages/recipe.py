import streamlit as st
import urllib.parse
import re
from openai import OpenAI
from typing import List, Dict

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = "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"
)

def generate_recipe_ai(ingredients: str, cuisine: str, diet: List[str]) -> str:
    """Generate recipe using AI with enhanced error handling"""
    try:
        diet_text = ", ".join(diet) if diet else "No specific dietary requirements"
        prompt = f"""Create a detailed recipe with these ingredients: {ingredients}
        Format strictly as:
        Title: [Creative Recipe Name]

        Ingredients:
        - Measurement Ingredient 1
        - Measurement Ingredient 2

        Instructions:
        1. Step 1
        2. Step 2

        Cuisine Style: {cuisine}
        Dietary Needs: {diet_text}
        Include precise measurements and cooking times."""

        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Recipe generation failed: {str(e)}")
        return ""

def parse_recipe(raw_text: str) -> Dict:
    """Improved recipe parsing with better error handling and pattern matching"""
    try:
        # Normalize text format
        normalized = re.sub(r'\n+', '\n', raw_text.strip())

        # Extract title using multiple possible patterns
        title_match = re.search(r'(?:Recipe:|Title:|^)(.*?)\n', normalized, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Chef's Special"

        # Extract ingredients using multiple possible patterns
        ingredients_section = re.search(
            r'(Ingredients:?|You\'ll need:?)(.*?)(?=\nInstructions:|Steps:|$)',
            normalized,
            re.DOTALL | re.IGNORECASE
        )
        ingredients = [i.strip() for i in ingredients_section.group(2).split('\n') if i.strip()] if ingredients_section else []

        # Improved instructions parsing
        instructions_section = re.search(
            r'(Instructions:?|Steps:?|Method:?|Directions:?)(.*?)(?=\n\n|$)',
            normalized,
            re.DOTALL | re.IGNORECASE
        )
        instructions = []
        if instructions_section:
            instructions = [
                re.sub(r'^\d+[\.\)]?\s*', '', s.strip())
                for s in instructions_section.group(2).split('\n')
                if s.strip() and len(s.strip()) > 10
            ]

        # Fallback if sections not found
        if not ingredients or not instructions:
            return {
                "title": title,
                "ingredients": ["Fresh creativity", "Pinch of magic"],
                "instructions": [raw_text]
            }

        return {
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions
        }
    except Exception as e:
        st.error(f"Error parsing recipe: {str(e)}")
        return {
            "title": "Chef's Special",
            "ingredients": ["Fresh creativity", "Pinch of magic"],
            "instructions": [raw_text]
        }

def recipe_page():
    """Main recipe page using expanders for each generated recipe"""
    if "recipes" not in st.session_state:
        st.session_state.recipes = []

    st.markdown("""
    <style>
        .recipe-card {
            background: var(--card);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        .recipe-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .recipe-title {
            color: var(--primary);
            margin: 0;
            font-size: 1.2rem;
        }
        .ingredient-list {
            list-style-type: none;
            padding-left: 0;
            margin-bottom: 1.5rem;
        }
        .instruction-step {
            padding: 0.8rem;
            background: var(--background);
            border-left: 3px solid var(--secondary);
            margin: 0.5rem 0;
            border-radius: 4px;
        }
        .header-image {
            border-radius: 8px;
            margin-left: 1rem;
            border: 2px solid var(--border);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="color: var(--primary); margin-bottom: 2rem;">🧑🍳 AI Recipe Generator</h1>', unsafe_allow_html=True)

    with st.form("recipe_form"):
        col1, col2 = st.columns([3, 2])
        with col1:
            ingredients = st.text_input(
                "Your Ingredients 🥕",
                placeholder="e.g., chicken, tomatoes, olive oil",
                help="Enter main ingredients separated by commas"
            )
            cuisine = st.selectbox(
                "Cuisine Style 🌍",
                ["Any", "Italian", "Asian", "Mexican", "Mediterranean", "French", "American"],
                index=0
            )
        with col2:
            diet = st.multiselect(
                "Dietary Preferences 🥦",
                ["Vegetarian", "Vegan", "Gluten-free", "Dairy-free", "Keto"],
                help="Select all that apply"
            )
            recipe_count = st.slider(
                "Number of Recipes 📚",
                1, 5, 3,
                help="Choose how many recipe variations to generate"
            )

        submitted = st.form_submit_button(
            "✨ Generate Magic Recipes ✨",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if ingredients.strip():
            with st.spinner("🧑🍳 Chef is working hard..."):
                try:
                    new_recipes = []
                    for _ in range(recipe_count):
                        raw_recipe = generate_recipe_ai(ingredients, cuisine, diet)
                        if raw_recipe:
                            parsed = parse_recipe(raw_recipe)
                            if parsed["ingredients"] and parsed["instructions"]:
                                new_recipes.append(parsed)

                    if new_recipes:
                        st.session_state.recipes = new_recipes
                        st.success(f"🎉 Successfully generated {len(new_recipes)} recipes!")
                    else:
                        st.warning("⚠️ No valid recipes generated. Try different ingredients!")
                except Exception as e:
                    st.error(f"🚨 Critical error: {str(e)}")
        else:
            st.warning("⚠️ Please enter some ingredients to get started!")

    # Display generated recipes as collapsible expander cards
    if st.session_state.recipes:
        st.markdown("---")
        st.markdown('<h2 style="color: var(--primary);">🍽️ Generated Recipes</h2>', unsafe_allow_html=True)

        for idx, recipe in enumerate(st.session_state.recipes):
            if not isinstance(recipe, dict):
                continue

            # # Create image URL based on title keywords (fallback to default)
            # try:
            #     title_text = recipe.get('title', 'food')
            #     # Extract keywords longer than 3 letters that are not generic
            #     keywords = [word for word in title_text.split() if len(word) > 3 and word.lower() not in ['recipe', 'food']]
            #     query = urllib.parse.quote('+'.join(keywords)) if keywords else "food"
            #     image_url = f"https://source.unsplash.com/400x300/?{query},food,cooking"
            # except Exception:
            #     image_url = "https://source.unsplash.com/400x300/?food"

            # Use a default title variable to avoid f-string escaping issues
            default_title = "Chef's Special"
            header_str = f"{recipe.get('title', default_title)} | Servings: 4 | Ratings: 4.5 ⭐"

            # Render the expander card - fixed the expander usage here
            with st.expander(header_str):
                # # Display the header image at the top of the expanded view.
                # st.image(image_url, caption=recipe.get('title', ''), use_container_width=True)
                st.markdown("#### 🥄 Ingredients")
                st.markdown(
                    "<ul class='ingredient-list'>" +
                    "".join([f"<li class='instruction-step'>✔️ {i}</li>" for i in recipe.get('ingredients', [])]) +
                    "</ul>",
                    unsafe_allow_html=True
                )
                st.markdown("#### 📝 Instructions")
                for step_index, step in enumerate(recipe.get('instructions', []), 1):
                    st.markdown(
                        f"<div class='instruction-step'><strong>Step {step_index}:</strong> {step}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("---")
