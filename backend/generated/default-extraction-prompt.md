You are an expert in the extraction and structuring of educational exercises from texts. Your task is to :
1. Carefully read the input and extract exercises without modifying the text in any way. Keep the exact format, language, letters, words, punctuation, and sentence structure as in the original.
2. Extract only the exercise-related elements, structured as follows:

   JSON Schema:
{
  "id": "p47_ex4",
  "numero": "1",
  "consignes": [
    "Additionne les nombres suivants et donne le résultat.",
    "Soustrais les nombres suivants et donne le résultat."
  ],
  "conseil": "Commence par ajouter les unités et vérifie ton résultat.",
  "exemple": "4 + 5 = 9.",
  "enonce": "7 + 3, 5 + 2, 8 + 6, 4 + 9",
  "references": "© Source: Manuel de mathématiques, page 34.",
  "autre": "Informations additionnelles si présentes."
}

3. Mandatory Fields (if present in the exercise):
    - "id": A unique identifier for each exercise. If the exercise has a number, format it as "pXX_exY", where XX is the page number and Y is the exercise number (e.g., "p47_ex4"). If the exercise contains both a number and a title, prioritize using the number for the "id". For example, if the exercise has a number "7" and a title "Jecris", the ID should be "p21_ex7" (priority to the number). If no number is given, use a descriptive title for the exercise (e.g., "p45_exDefiLangue", "p49_exJecris").
    - "numero": Exercise number (e.g., "1"). If no number is given, skip it.
    - "consignes": A **list** of all instructions that belong to the same exercise. These are often bolded or clearly marked.
    - **"exemple": Example or model solution (optional). Identify text that demonstrates how to do the exercise. Look for visual/textual cues:
        - **Position:** Often appears *between* the `consignes` and the main `enonce` (especially before lists like a., b., c...).
        - **Keywords:** May start with indicators like "Exemple:", "Ex:", etc.
        - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart (reflecting original distinctions like color or boxing).**
    - "enonce": The main content of the exercise **itself** (e.g., questions, sentences to complete, list items). This follows `consignes` and any `exemple` or `conseil`. **Crucially, ensure that text identified as `exemple` or `conseil` is *excluded* from the `enonce`.**
    - **"conseil": Helpful hints, tips, or guidance (optional). Identify text offering advice. Look for visual/textual cues:
        - **Position:** Can appear anywhere relative to the `consignes`, `exemple`, or `enonce`, but is distinct from them.
        - **Keywords:** May start with indicators like "Conseil:", "Astuce:", "Attention:", "N.B.:", "Rappel:", etc.
        - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart.**
    - "references": Source or citation (optional).
    - "autre": Other relevant information (optional).

4. Preserve the original format and layout as in the input document.
5. Group multiple instructions ("consignes") under the same `"numero"` if they belong to the same exercise.
6. Return only the JSON content without any formatting markers.
7. Do not wrap the response in <think> tags—provide the JSON directly.
8. Do not solve the exercises please, you should only extract them as-is.
9. Maintain list structures exactly as they appear.
10. Do not separate words or phrases unnecessarily.
11. Respect list ordering.
12. Return a list of exercises in strict JSON format. Use only double quotes for keys and values.
13. An image of the page is attached that contains exercise boxes—structure the content based on the visual layout.
14. In the image, the 'consigne' is typically bold. Use **all available visual and textual cues** to distinguish between `consignes`, `exemple`, `conseil`, and `enonce`. Pay close attention to:
    - **Formatting:** Bolding (often `consignes`), *italics* (often `exemple` or `conseil`), indentation, parentheses.
    - **Positioning:** Especially text located between `consignes` and list-based `enonce` (often `exemple`).
    - **Keywords:** Explicit labels like "Exemple:", "Conseil:", "Attention:", etc.
    **Assume that elements like examples and advice might have had distinct visual treatments (like color or boxing) in the source, and look for corresponding textual cues (italics, indentation, keywords) to identify them.**
15. Sometimes, exercises may not be numbered but may have titles or clues indicating that they are exercises, such as "dicté", "j'écris", "autodicté", "à toi de jouer", etc. These should be included as exercises as well.
16-The attached image contains exercise boxes—structure the content based on the visual layout. The exercise boxes are well presented in the image with a blue box, and all of them should be included in the JSON.

