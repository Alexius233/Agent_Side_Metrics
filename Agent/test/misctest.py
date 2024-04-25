
from llama_index.llms import ChatMessage
import re
"""
message = "hello world"
message1 = "test message"

his = ChatMessage(role="user", content=message)
his1 = ChatMessage(role="system", content=message1)
history = []

history.append(his)
history.append(his1)

#print(history)

print(history[0].role.value)
"""


protrait = """
Based on the movie watching history provided, here is an enhanced user portrait for User ID: 1:

User ID: 1

Emotional Resonance: Enjoys the thrill of adventure and intense drama

Narrative Preferences: Prefers complex, multi-threaded narratives with significant character development

Thematic Exploration: Drawn to themes of exploration, personal growth, and overcoming adversity

Visual and Aesthetic Preferences: Appreciates movies with groundbreaking visual effects and unique visual storytelling

Based on the user's watching history, we can infer that User ID: 1 enjoys movies that offer a mix of adventure, excitement, and emotional depth. They seem to prefer complex narratives with well-developed characters, and are drawn to themes of exploration, personal growth, and overcoming adversity. Additionally, they appreciate movies with groundbreaking visual effects and unique visual storytelling.

The user's first movie watched, "Toy Story" (1995), is an adventure comedy film that follows a group of toys as they navigate through a magical board game. This movie aligns with User ID: 1's preference for adventure and excitement, and its complex narrative structure with well-developed characters also fits their preference.

The second movie watched, "The American President" (1995), is a romantic comedy-drama film that explores themes of love, politics, and personal growth. This movie aligns with User ID: 1's interest in themes of personal growth and overcoming adversity, and its character-driven narrative also fits their preference.

The third movie watched, "Get Shorty" (1995), is a crime comedy-thriller film that follows a criminal psychologist and a detective as they team up to catch a serial killer. This movie aligns with User ID: 1's preference for complex narratives with well-developed characters, and its crime and thriller elements also fit their interest in adventure and excitement.

Overall, User ID: 1's movie watching history suggests that they enjoy a mix of adventure, comedy, and drama with complex narratives and well-developed characters. They also appreciate movies"""

"""
pattern = r"(User ID:.+?Visual and Aesthetic Preferences:.+?)\n"

# 使用 re.DOTALL 以确保 . 匹配包括换行符在内的任意字符
match = re.search(pattern, protrait, re.DOTALL)

if match:
    extracted_text = match.group(1)  # 提取匹配的文本
    cleaned_text = re.sub(r"^User ID: \d+:\n\n", "", extracted_text, flags=re.MULTILINE)

    print(cleaned_text)
else:
    print("No match found")
"""

text = """
Summary:

The user analyst report indicates that User ID 1 tends to seek movies that elicit a range of emotions, including drama, romance, and comedy, with a preference for character-driven narratives that explore themes of love, relationships, and personal identity. User ID 2 typically seeks movies that offer excitement, adventure, and comedy, with a preference for complex, multi-threaded narratives that keep them engaged and invested in the story.

The movie analyst report highlights "The Shawshank Redemption" as a high-appeal movie with a timeless classic status, featuring themes of hope, redemption, and the human spirit. The core audience for this movie is likely to be viewers who enjoy movies that elicit a range of emotions, with a preference for characters-driven stories and complex, multi-threaded narratives.

Query for user analyst:
Can you provide more information on User ID 1's preferences for comedy movies? Are they more into light-hearted comedies or darker, edgier comedies?

Query for movie analyst:
Can you provide more information on the specific themes and narrative elements that make "The Shawshank Redemption" a timeless classic? How do these elements contribute to its high appeal and emotional resonance?

X
"""

user_analyst_query = re.search(r"Query for user analyst:\n(.*?)\n", text, re.DOTALL)
if user_analyst_query:
    print(user_analyst_query.group(1).strip())

# 提取“Query for movie analyst:”后，直到第一个换行符的内容
movie_analyst_query = re.search(r"Query for movie analyst:\n(.*?)\n", text, re.DOTALL)
if movie_analyst_query:
    print(movie_analyst_query.group(1).strip())
    