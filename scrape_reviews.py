import requests
import json
import os
import time

# RMP uses GraphQL internally - these are the exact queries the website uses
HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Content-Type": "application/json",
}

REVIEWS_QUERY = """
query RatingsListQuery($count: Int!, $id: ID!, $cursor: String) {
  node(id: $id) {
    ... on Teacher {
      ratings(first: $count, after: $cursor) {
        edges {
          node {
            comment
            class
            date
            helpfulRating
            clarityRating
            difficultyRating
            wouldTakeAgain
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
"""

def get_reviews(professor_id, professor_name, max_reviews=50):
    """Fetch reviews for a professor using RMP's GraphQL API"""
    
    # RMP uses base64 encoded IDs
    import base64
    encoded_id = base64.b64encode(f"Teacher-{professor_id}".encode()).decode()
    
    all_reviews = []
    cursor = None
    
    while len(all_reviews) < max_reviews:
        variables = {
            "count": min(20, max_reviews - len(all_reviews)),
            "id": encoded_id,
            "cursor": cursor
        }
        
        response = requests.post(
            "https://www.ratemyprofessors.com/graphql",
            headers=HEADERS,
            json={"query": REVIEWS_QUERY, "variables": variables}
        )
        
        if response.status_code != 200:
            print(f"Error fetching {professor_name}: {response.status_code}")
            break
            
        data = response.json()
        
        try:
            ratings = data["data"]["node"]["ratings"]
            edges = ratings["edges"]
            
            for edge in edges:
                node = edge["node"]
                if node["comment"] and node["comment"].strip():
                    all_reviews.append(node)
            
            page_info = ratings["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]
            
        except (KeyError, TypeError) as e:
            print(f"Error parsing response for {professor_name}: {e}")
            break
        
        time.sleep(1)  # be polite, avoid rate limiting
    
    return all_reviews

def save_professor_reviews(professor_name, professor_id, filename):
    """Fetch and save reviews to a text file"""
    print(f"Fetching reviews for {professor_name}...")
    reviews = get_reviews(professor_id, professor_name, max_reviews=50)
    
    if not reviews:
        print(f"  No reviews found for {professor_name}")
        return
    
    with open(f"documents/{filename}", "w", encoding="utf-8") as f:
        f.write(f"Professor: {professor_name}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, review in enumerate(reviews, 1):
            f.write(f"Review {i}:\n")
            f.write(f"Class: {review.get('class', 'N/A')}\n")
            f.write(f"Rating: Clarity {review.get('clarityRating')}/5, ")
            f.write(f"Difficulty {review.get('difficultyRating')}/5\n")
            f.write(f"Comment: {review.get('comment', '').strip()}\n")
            f.write("\n---\n\n")
    
    print(f"  Saved {len(reviews)} reviews to documents/{filename}")

# Your 10 professors - (name, RMP professor ID, filename)
professors = [
    ("Susan Nachawati",      115586,  "nachawati_susan.txt"),
    ("Ali Sharifian",        2300819, "sharifian_ali.txt"),
    ("Alireza Mehrnia",      2521315, "mehrnia_alireza.txt"),
    ("Jelena Trajkovic",     2493982, "trajkovic_jelena.txt"),
    ("Shannon Cleary",       1287692, "cleary_shannon.txt"),
    ("Chant Phengpis",       934194,  "phengpis_chant.txt"),
    ("Xiaoying (Cindy) Chen",917849,  "chen_xiaoying.txt"),
    ("Frank McEnulty",       2088803, "mcenulty_frank.txt"),
    ("Wikrom Prombutr",      1781246, "prombutr_wikrom.txt"),
    ("Aslihan Salih",        2626180, "salih_aslihan.txt"),
]

if __name__ == "__main__":
    os.makedirs("documents", exist_ok=True)
    for name, prof_id, filename in professors:
        save_professor_reviews(name, prof_id, filename)
        time.sleep(2)  # pause between professors
    print("\nDone! Check your documents/ folder.")