#!/usr/bin/env python3
"""
Social Media Sentiment & Engagement Dataset Generator
Assignment 6: Handling unstructured/semi-structured data and visualizing patterns

Generates 420 synthetic posts spanning 2026-03-01 to 2026-08-31 with realistic
distributions, engagement spikes, and sentiment patterns.
"""

import json
import csv
import random
from datetime import datetime, timedelta
from collections import Counter

random.seed(42)

PLATFORMS = ["Twitter", "Instagram", "Facebook", "LinkedIn", "YouTube"]
USER_TYPES = ["Regular", "Influencer", "Brand", "Verified"]
TOPICS = ["Product Launch", "Customer Service", "Marketing Campaign", "Tech Review", "Lifestyle", "Sports", "Entertainment", "News"]
HASHTAG_POOL = [
    "#TechLaunch", "#CustomerLove", "#BrandCampaign", "#Review", "#Lifestyle",
    "#SportsDay", "#Entertainment", "#BreakingNews", "#Innovation", "#Sale",
    "#NewProduct", "#Feedback", "#Trending", "#Viral", "#MustHave",
    "#Quality", "#Support", "#Update", "#Community", "#Event2026"
]
LANGUAGES = ["en"]

# Sentiment templates: (text, sentiment_label, score_range)
TEXT_TEMPLATES = {
    "positive": [
        "Absolutely love the new {topic}! The quality is outstanding and delivery was super fast. Highly recommend! {hashtags}",
        "Amazing experience with {topic} – customer support went above and beyond. 5 stars! {hashtags}",
        "This {topic} campaign is everything! Creative, inspiring and so well executed. {hashtags}",
        "Just tried the new feature and I'm blown away. Clean UI, smooth performance! {hashtags}",
        "Shoutout to the team behind {topic} – you nailed it. Can't wait for what's next! {hashtags}",
        "Love how {topic} keeps innovating. Best update this quarter! {hashtags}",
        "Fantastic {topic} event today! Great speakers and networking opportunities. {hashtags}",
        "My favorite {topic} ever. Worth every penny! {hashtags}",
    ],
    "negative": [
        "Really disappointed with {topic}. The product arrived damaged and support hasn't replied in 3 days. {hashtags}",
        "Not impressed by {topic} – overpriced and underwhelming. Expected much better. {hashtags}",
        "Worst experience with {topic} customer service. Long wait, no resolution. {hashtags}",
        "This {topic} update broke everything. App keeps crashing now. Fix ASAP! {hashtags}",
        "Misleading advertising for {topic}. What was promised vs delivered is very different. {hashtags}",
        "Cancelled my order for {topic}. Too many delays and poor communication. {hashtags}",
        "The {topic} event was chaotic and poorly organized. Waste of time. {hashtags}",
        "Avoid {topic} – quality control issues and no refund. {hashtags}",
    ],
    "neutral": [
        "Checking out the new {topic} update. Some interesting changes, still exploring. {hashtags}",
        "Attended the {topic} webinar today. Covered basics, Q&A was decent. {hashtags}",
        "Here's my unboxing of {topic}. First impressions in thread. {hashtags}",
        "Comparison: {topic} vs competitors – specs, pricing and availability. {hashtags}",
        "Update on {topic}: rollout scheduled next week across all regions. {hashtags}",
        "Live from the {topic} venue. Crowd size looks moderate. {hashtags}",
        "Documenting my week with {topic}. Day 3 observations. {hashtags}",
        "Info session about {topic} – slides shared in comments. {hashtags}",
    ]
}

def generate_text(topic, sentiment):
    template = random.choice(TEXT_TEMPLATES[sentiment])
    hashtags = " ".join(random.sample(HASHTAG_POOL, random.randint(1,3)))
    text = template.format(topic=topic.lower(), hashtags=hashtags)
    # Add some semi-structured noise: mentions, urls, emojis simulation
    if random.random() < 0.35:
        text += f" @{random.choice(['brand','support','official','team'])}"
    if random.random() < 0.25:
        text += " https://t.co/example123"
    return text

def generate_post(idx, date):
    platform = random.choices(PLATFORMS, weights=[30, 25, 20, 12, 13], k=1)[0]
    topic = random.choice(TOPICS)
    user_type = random.choices(USER_TYPES, weights=[55, 15, 20, 10], k=1)[0]
    
    # Sentiment distribution skewed by topic & platform
    # Product Launch & Marketing Campaign more positive, Customer Service more negative, LinkedIn more neutral/positive
    if topic in ["Product Launch", "Marketing Campaign"]:
        sentiment_weights = [55, 25, 20]  # pos, neutral, neg
    elif topic == "Customer Service":
        sentiment_weights = [20, 30, 50]
    elif platform == "LinkedIn":
        sentiment_weights = [40, 45, 15]
    elif platform == "Twitter":
        sentiment_weights = [35, 30, 35]
    else:
        sentiment_weights = [42, 32, 26]
    
    sentiment_label = random.choices(["positive", "neutral", "negative"], weights=sentiment_weights, k=1)[0]
    
    if sentiment_label == "positive":
        sentiment_score = round(random.uniform(0.55, 0.98), 3)
    elif sentiment_label == "negative":
        sentiment_score = round(random.uniform(-0.98, -0.55), 3)
    else:
        sentiment_score = round(random.uniform(-0.35, 0.35), 3)
    
    # Engagement generation with spikes
    base_likes = {"Twitter": (20, 800), "Instagram": (80, 2500), "Facebook": (30, 1200), "LinkedIn": (15, 600), "YouTube": (40, 1500)}
    base_shares = {"Twitter": (5, 300), "Instagram": (5, 200), "Facebook": (10, 400), "LinkedIn": (2, 150), "YouTube": (5, 250)}
    base_comments = {"Twitter": (3, 200), "Instagram": (10, 400), "Facebook": (5, 300), "LinkedIn": (2, 120), "YouTube": (10, 600)}
    
    # Day-of-week and event spikes
    is_weekend = date.weekday() >= 5
    is_campaign_peak = date in [datetime(2026, 4, 15), datetime(2026, 5, 20), datetime(2026, 6, 10), datetime(2026, 7, 18)]
    is_negative_viral = (sentiment_label == "negative" and random.random() < 0.12)
    is_positive_viral = (sentiment_label == "positive" and user_type == "Influencer" and random.random() < 0.25)
    
    def gen_engagement(low, high, multiplier=1.0):
        val = random.randint(low, high)
        if is_campaign_peak:
            val = int(val * random.uniform(2.0, 3.5))
        if is_weekend and platform in ["Instagram", "YouTube"]:
            val = int(val * 1.4)
        if is_positive_viral:
            val = int(val * random.uniform(2.5, 5.0))
        if is_negative_viral:
            val = int(val * random.uniform(1.8, 3.2))
        if user_type == "Influencer":
            val = int(val * 1.6)
        if user_type == "Brand":
            val = int(val * 1.3)
        return val
    
    likes = gen_engagement(*base_likes[platform])
    shares = gen_engagement(*base_shares[platform])
    comments = gen_engagement(*base_comments[platform])
    views = likes * random.randint(8, 25) + random.randint(0, 5000)
    
    # Engagement rate
    engagement_rate = round((likes + shares + comments) / max(views, 1) * 100, 2)
    
    text = generate_text(topic, sentiment_label)
    hashtags = random.sample(HASHTAG_POOL, random.randint(1, 4))
    
    # Timestamp with hour distribution (peak 10am-10pm)
    hour_weights = [2,1,1,1,1,2,4,8,12,15,18,20,20,18,16,15,18,20,22,18,12,8,5,3]
    hour = random.choices(list(range(24)), weights=hour_weights, k=1)[0]
    minute = random.randint(0, 59)
    timestamp = date.replace(hour=hour, minute=minute, second=random.randint(0,59))
    
    return {
        "post_id": f"P{idx:04d}",
        "platform": platform,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "date": timestamp.strftime("%Y-%m-%d"),
        "hour": hour,
        "text": text,
        "likes": likes,
        "shares": shares,
        "comments": comments,
        "views": views,
        "engagement": likes + shares + comments,
        "engagement_rate": engagement_rate,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "hashtags": hashtags,
        "hashtags_str": " ".join(hashtags),
        "topic": topic,
        "user_type": user_type,
        "verified": user_type in ["Verified", "Brand"] or (user_type == "Influencer" and random.random() < 0.6),
        "language": "en"
    }

def main():
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 8, 31)
    num_posts = 420
    
    dates = []
    current = start_date
    while current <= end_date:
        # More posts around campaign peaks and weekends on Instagram
        weight = 1.0
        if current.weekday() in [4,5,6]:  # Fri-Sun higher
            weight = 1.3
        if current.month in [4, 5, 6,7]: # campaign months higher
            weight = weight * 1.2
        dates.append((current, weight))
        current += timedelta(days=1)
    
    # Sample dates weighted
    total_weight = sum(w for _, w in dates)
    probs = [w/total_weight for _, w in dates]
    date_list = [d for d,_ in dates]
    chosen_dates = random.choices(date_list, weights=probs, k=num_posts)
    chosen_dates.sort()
    
    posts = []
    for i, d in enumerate(chosen_dates, start=1):
        posts.append(generate_post(i, d))
    
    # Sort by timestamp
    posts.sort(key=lambda x: x["timestamp"])
    # Reassign post_id in chronological order
    for i, p in enumerate(posts, start=1):
        p["post_id"] = f"P{i:04d}"
    
    # Export JSON
    with open("/mnt/e/DSA0606-asmt/data/social_media_dataset.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    # Export CSV
    fieldnames = list(posts[0].keys())
    # Convert hashtags list to string for CSV is already hashtags_str, but keep both
    # For CSV export, hashtags as string
    with open("/mnt/e/DSA0606-asmt/data/social_media_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in posts:
            row = p.copy()
            row["hashtags"] = ", ".join(p["hashtags"])
            writer.writerow(row)
    
    # Print stats
    print(f"Generated {len(posts)} posts")
    print("Platform:", Counter(p["platform"] for p in posts))
    print("Sentiment:", Counter(p["sentiment_label"] for p in posts))
    print("Topic:", Counter(p["topic"] for p in posts))
    print("User type:", Counter(p["user_type"] for p in posts))
    total_eng = sum(p["engagement"] for p in posts)
    print(f"Total engagement: {total_eng:,}")
    print(f"Date range: {posts[0]['date']} to {posts[-1]['date']}")
    # Also write a stats JSON for report
    stats = {
        "total_posts": len(posts),
        "platform_dist": dict(Counter(p["platform"] for p in posts)),
        "sentiment_dist": dict(Counter(p["sentiment_label"] for p in posts)),
        "topic_dist": dict(Counter(p["topic"] for p in posts)),
        "user_type_dist": dict(Counter(p["user_type"] for p in posts)),
        "total_engagement": total_eng,
        "avg_sentiment": round(sum(p["sentiment_score"] for p in posts)/len(posts), 3),
        "date_range": f"{posts[0]['date']} to {posts[-1]['date']}"
    }
    with open("/mnt/e/DSA0606-asmt/data/dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
if __name__ == "__main__":
    main()
