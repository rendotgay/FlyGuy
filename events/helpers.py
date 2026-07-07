from db import get_db


def get_weed_rank(userid) -> str:
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT total_entries * 1.0 / total_gifs
        FROM (
            SELECT user1, COUNT(*) AS total_entries
            FROM gifs
            GROUP BY user1
        ) AS user_counts
        CROSS JOIN (SELECT COUNT(*) AS total_gifs FROM gifs) AS total_count
        WHERE user1 = ?;
    """

    cursor.execute(query, (userid,))
    result = cursor.fetchone()

    if result is None or result[0] is None:
        return "Marijuana Mystery"  # User not found

    score = result[0]  # This is total_entries / total_gifs

    if score >= 0.5:
        return "Blaze Boss 👑"
    elif score >= 0.45:
        return "Weed Wizard 🧙‍♂️"
    elif score >= 0.4:
        return "Puff Prophet 🔮"
    elif score >= 0.35:
        return "Ganja Guru 🧘‍♂️"
    elif score >= 0.3:
        return "Rasta Rockstar 🎸"
    elif score >= 0.25:
        return "Joint Juggernaut 💪"
    elif score >= 0.2:
        return "Hazy Hero 🦸‍♂️"
    elif score >= 0.15:
        return "Toke Trainee 🌿"
    elif score >= 0.1:
        return "Puff Peasant 👩‍🌾"
    else:
        return "Newbie Nug 🌱"